from datetime import datetime
from typing import List

import psycopg2
from database import get_connection
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import MatchCreate, Player, PlayerCreate, ScoreUpdate
from psycopg2.extras import RealDictCursor

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Player endpoints
@app.get("/players", response_model=List[Player])
async def get_players():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""SELECT * FROM players ORDER BY player_name""")
        players = cur.fetchall()
        return players
    finally:
        cur.close()
        conn.close()


@app.post("/players", response_model=Player)
async def create_player(player: PlayerCreate):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            """
            INSERT INTO players (player_name)
            VALUES (%s)
            RETURNING *
            """,
            (player.player_name,),
        )
        new_player = cur.fetchone()
        conn.commit()
        return new_player
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()


# Match endpoints
@app.get("/matches")
async def get_matches():
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(
                """
                SELECT
                m.*, p1.player_name as team1_player1_name,
                p2.player_name as team1_player2_name,
                p3.player_name as team2_player1_name,
                p4.player_name as team2_player2_name
                FROM matches m
                LEFT JOIN players p1 ON m.team1_player1_id = p1.player_id
                LEFT JOIN players p2 ON m.team1_player2_id = p2.player_id
                LEFT JOIN players p3 ON m.team2_player1_id = p3.player_id
                LEFT JOIN players p4 ON m.team2_player2_id = p4.player_id
                ORDER BY m.match_date DESC
                """
            )
            matches = cur.fetchall()
            return matches
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Error in get_matches: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/matches")
async def create_match(match: MatchCreate):
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            # Validate 2v2 match requirements
            if match.match_type == "2v2":
                if not all(
                    [
                        match.team1_player1_id,
                        match.team1_player2_id,
                        match.team2_player1_id,
                        match.team2_player2_id,
                    ]
                ):
                    raise HTTPException(
                        status_code=422,
                        detail="2v2 matches require all player positions to be filled",
                    )

                # Check if same player is selected multiple times
                players = [
                    match.team1_player1_id,
                    match.team1_player2_id,
                    match.team2_player1_id,
                    match.team2_player2_id,
                ]
                if len(set(players)) != 4:
                    raise HTTPException(
                        status_code=422,
                        detail="Cannot use the same player multiple times in a match",
                    )

            # For 1v1 matches, ensure second player slots are null
            if match.match_type == "1v1":
                if match.team1_player2_id is not None or match.team2_player2_id is not None:
                    raise HTTPException(status_code=422, detail="1v1 matches should not have secondary players")
                match.team1_player2_id = None
                match.team2_player2_id = None

            # Validate players exist in database
            player_ids = [match.team1_player1_id, match.team2_player1_id]
            if match.match_type == "2v2":
                player_ids.extend([match.team1_player2_id, match.team2_player2_id])

            cur.execute("SELECT player_id FROM players WHERE player_id = ANY(%s)", (player_ids,))
            found_players = cur.fetchall()
            if len(found_players) != len(set(player_ids)):
                raise HTTPException(status_code=422, detail="One or more players not found in database")

            # Set scheduled_date to match_date if not provided
            scheduled_date = match.scheduled_date or match.match_date

            # Validate scores for completed matches
            status = "COMPLETED" if match.team1_goals is not None and match.team2_goals is not None else "SCHEDULED"
            if status == "COMPLETED":
                if match.team1_goals < 0 or match.team2_goals < 0:
                    raise HTTPException(status_code=422, detail="Goals cannot be negative")
            elif status == "SCHEDULED":
                # Ensure goals are null for scheduled matches
                match.team1_goals = None
                match.team2_goals = None

            # Calculate result for completed matches
            result = None
            if status == "COMPLETED":
                if match.team1_goals > match.team2_goals:
                    result = "Team1"
                elif match.team2_goals > match.team1_goals:
                    result = "Team2"
                else:
                    result = "Draw"

            # Validate match date
            if match.match_date < datetime.now() and status == "SCHEDULED":
                raise HTTPException(status_code=422, detail="Scheduled matches cannot be in the past")

            # Insert match
            cur.execute(
                """
                INSERT INTO matches (
                    round, match_type,
                    team1_player1_id, team1_player2_id,
                    team2_player1_id, team2_player2_id,
                    match_date, scheduled_date,
                    team1_goals, team2_goals,
                    status, result
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """,
                (
                    match.round,
                    match.match_type,
                    match.team1_player1_id,
                    match.team1_player2_id,
                    match.team2_player1_id,
                    match.team2_player2_id,
                    match.match_date,
                    scheduled_date,
                    match.team1_goals,
                    match.team2_goals,
                    status,
                    result,
                ),
            )
            new_match = cur.fetchone()

            # If match is completed, player stats will be updated by the trigger
            conn.commit()
            return new_match
        except psycopg2.Error as e:
            conn.rollback()
            print(f"Database error in create_match: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Error in create_match: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/matches/{match_id}")
async def update_match(match_id: int, match: MatchCreate):
    print(f"Received update request for match {match_id}")
    print(f"Request data: {match.dict()}")
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            # Check if match exists and get current data
            cur.execute("SELECT * FROM matches WHERE id = %s", (match_id,))
            existing_match = cur.fetchone()
            if not existing_match:
                raise HTTPException(status_code=404, detail="Match not found")

            print(f"Existing match data: {existing_match}")

            # If both goals are provided in the update, use them
            # If only one goal is provided, consider it invalid
            if match.team1_goals is not None and match.team2_goals is not None:
                status = "COMPLETED"
                team1_goals = match.team1_goals
                team2_goals = match.team2_goals
                if team1_goals > team2_goals:
                    result = "Team1"
                elif team2_goals > team1_goals:
                    result = "Team2"
                else:
                    result = "Draw"
            # If no goals are provided, keep existing goals or null
            else:
                status = "SCHEDULED"
                team1_goals = None
                team2_goals = None
                result = None

            print(f"Status: {status}, Result: {result}, Goals: {team1_goals}-{team2_goals}")

            # Update match
            cur.execute(
                """
                UPDATE matches
                SET round = %s,
                    match_type = %s,
                    team1_player1_id = %s,
                    team1_player2_id = %s,
                    team2_player1_id = %s,
                    team2_player2_id = %s,
                    match_date = %s,
                    team1_goals = %s,
                    team2_goals = %s,
                    status = %s,
                    result = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING *
            """,
                (
                    match.round,
                    match.match_type,
                    match.team1_player1_id,
                    match.team1_player2_id,
                    match.team2_player1_id,
                    match.team2_player2_id,
                    match.match_date,
                    team1_goals,
                    team2_goals,
                    status,
                    result,
                    match_id,
                ),
            )

            updated_match = cur.fetchone()
            if not updated_match:
                raise HTTPException(status_code=404, detail="Failed to update match")

            conn.commit()
            print(f"Successfully updated match: {updated_match}")
            return updated_match

        except Exception as e:
            conn.rollback()
            print(f"Database error in update_match: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Error in update_match: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/matches/{match_id}/score")
async def update_match_score(match_id: int, score: ScoreUpdate):
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            # First get the current match status
            cur.execute("SELECT status FROM matches WHERE id = %s", (match_id,))
            current_match = cur.fetchone()
            if not current_match:
                raise HTTPException(status_code=404, detail="Match not found")

            # Calculate result based on scores
            team1_goals = score.team1_goals  # Use direct attribute access instead of .get()
            team2_goals = score.team2_goals

            if team1_goals > team2_goals:
                result = "Team1"
            elif team2_goals > team1_goals:
                result = "Team2"
            else:
                result = "Draw"

            # Update match
            cur.execute(
                """
                UPDATE matches
                SET team1_goals = %s,
                    team2_goals = %s,
                    status = 'COMPLETED',
                    result = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING *
            """,
                (team1_goals, team2_goals, result, match_id),
            )

            updated_match = cur.fetchone()
            if not updated_match:
                raise HTTPException(status_code=404, detail="Match not found")

            conn.commit()
            return updated_match
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Error in update_match_score: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/matches/{match_id}")
async def delete_match(match_id: int):
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            # First check if match exists and its status
            cur.execute("SELECT status FROM matches WHERE id = %s", (match_id,))
            match = cur.fetchone()
            if not match:
                raise HTTPException(status_code=404, detail="Match not found")

            # Delete match
            cur.execute("DELETE FROM matches WHERE id = %s RETURNING *", (match_id,))
            deleted_match = cur.fetchone()

            conn.commit()
            return deleted_match
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Error in delete_match: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/standings")
async def get_standings():
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            # Get Round 1 standings (1v1 matches)
            cur.execute(
                """
                WITH round1_stats AS (
                    SELECT
                        p.player_id,
                        p.player_name,
                        COUNT(*) as matches_played,
                        SUM(CASE
                            WHEN (m.team1_player1_id = p.player_id AND COALESCE(m.team1_goals, 0)
                                    > COALESCE(m.team2_goals, 0)) OR
                                 (m.team2_player1_id = p.player_id AND COALESCE(m.team2_goals, 0)
                                    > COALESCE(m.team1_goals, 0))
                                 THEN 1
                            ELSE 0
                        END) as wins,
                        SUM(CASE
                            WHEN COALESCE(m.team1_goals, 0) = COALESCE(m.team2_goals, 0) THEN 1
                            ELSE 0
                        END) as draws,
                        SUM(CASE
                            WHEN (m.team1_player1_id = p.player_id AND COALESCE(m.team1_goals, 0)
                                    < COALESCE(m.team2_goals, 0)) OR
                                 (m.team2_player1_id = p.player_id AND COALESCE(m.team2_goals, 0)
                                    < COALESCE(m.team1_goals, 0)) THEN 1
                            ELSE 0
                        END) as losses,
                        SUM(CASE
                            WHEN m.team1_player1_id = p.player_id THEN COALESCE(m.team1_goals, 0)
                            ELSE COALESCE(m.team2_goals, 0)
                        END) as goals_scored,
                        SUM(CASE
                            WHEN m.team1_player1_id = p.player_id THEN COALESCE(m.team2_goals, 0)
                            ELSE COALESCE(m.team1_goals, 0)
                        END) as goals_against
                    FROM players p
                    LEFT JOIN matches m ON (
                        m.team1_player1_id = p.player_id OR
                        m.team2_player1_id = p.player_id
                    )
                    WHERE m.match_type = '1v1'
                    AND m.round = 'Round 1'
                    AND m.status = 'COMPLETED'
                    GROUP BY p.player_id, p.player_name
                )
                SELECT
                    player_id,
                    player_name,
                    matches_played,
                    wins * 6 + draws * 2 as points,
                    wins,
                    draws,
                    losses,
                    goals_scored,
                    goals_against,
                    goals_scored - goals_against as goal_difference
                FROM round1_stats
                WHERE matches_played > 0
                ORDER BY points DESC, goal_difference DESC
            """
            )
            round1_standings = cur.fetchall()

            # Get Round 2 standings (2v2 matches)
            cur.execute(
                """
                WITH round2_stats AS (
                    SELECT
                        p.player_id,
                        p.player_name,
                        COUNT(*) as matches_played,
                        SUM(CASE
                            WHEN ((m.team1_player1_id = p.player_id OR m.team1_player2_id = p.player_id)
                                  AND COALESCE(m.team1_goals, 0) > COALESCE(m.team2_goals, 0)) OR
                                 ((m.team2_player1_id = p.player_id OR m.team2_player2_id = p.player_id)
                                  AND COALESCE(m.team2_goals, 0) > COALESCE(m.team1_goals, 0)) THEN 1
                            ELSE 0
                        END) as wins,
                        SUM(CASE
                            WHEN COALESCE(m.team1_goals, 0) = COALESCE(m.team2_goals, 0) THEN 1
                            ELSE 0
                        END) as draws,
                        SUM(CASE
                            WHEN ((m.team1_player1_id = p.player_id OR m.team1_player2_id = p.player_id)
                                  AND COALESCE(m.team1_goals, 0) < COALESCE(m.team2_goals, 0)) OR
                                 ((m.team2_player1_id = p.player_id OR m.team2_player2_id = p.player_id)
                                  AND COALESCE(m.team2_goals, 0) < COALESCE(m.team1_goals, 0)) THEN 1
                            ELSE 0
                        END) as losses,
                        SUM(CASE
                            WHEN m.team1_player1_id = p.player_id OR m.team1_player2_id = p.player_id
                                THEN COALESCE(m.team1_goals, 0)
                            ELSE COALESCE(m.team2_goals, 0)
                        END) as goals_scored,
                        SUM(CASE
                            WHEN m.team1_player1_id = p.player_id OR m.team1_player2_id = p.player_id
                                THEN COALESCE(m.team2_goals, 0)
                            ELSE COALESCE(m.team1_goals, 0)
                        END) as goals_against
                    FROM players p
                    LEFT JOIN matches m ON (
                        m.team1_player1_id = p.player_id OR
                        m.team1_player2_id = p.player_id OR
                        m.team2_player1_id = p.player_id OR
                        m.team2_player2_id = p.player_id
                    )
                    WHERE m.match_type = '2v2'
                    AND m.round = 'Round 2'
                    AND m.status = 'COMPLETED'
                    GROUP BY p.player_id, p.player_name
                )
                SELECT
                    player_id,
                    player_name,
                    matches_played,
                    wins * 3 + draws as points,
                    wins,
                    draws,
                    losses,
                    goals_scored,
                    goals_against,
                    goals_scored - goals_against as goal_difference
                FROM round2_stats
                WHERE matches_played > 0
                ORDER BY points DESC, goal_difference DESC
            """
            )
            round2_standings = cur.fetchall()

            # Calculate Tournament Standings
            tournament_standings = []
            for player in round1_standings:
                round2_player = next((p for p in round2_standings if p["player_id"] == player["player_id"]), None)
                if round2_player:
                    total_matches = player["matches_played"] + round2_player["matches_played"]
                    total_points = player["points"] + round2_player["points"]
                    total_wins = player["wins"] + round2_player["wins"]
                    total_draws = player["draws"] + round2_player["draws"]
                    total_losses = player["losses"] + round2_player["losses"]
                    total_goals_scored = player["goals_scored"] + round2_player["goals_scored"]
                    total_goals_against = player["goals_against"] + round2_player["goals_against"]
                    total_goal_difference = total_goals_scored - total_goals_against
                    tournament_standings.append(
                        {
                            "player_id": player["player_id"],
                            "player_name": player["player_name"],
                            "matches_played": total_matches,
                            "points": total_points,
                            "wins": total_wins,
                            "draws": total_draws,
                            "losses": total_losses,
                            "goals_scored": total_goals_scored,
                            "goals_against": total_goals_against,
                            "goal_difference": total_goal_difference,
                        }
                    )
                else:
                    tournament_standings.append(player)

            tournament_standings.sort(key=lambda x: (-x["points"], -x["goal_difference"]))

            return {
                "tournament": tournament_standings,
                "round1": round1_standings,
                "round2": round2_standings,
            }
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Error in get_standings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/overview")
async def get_overview_stats():
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            # Get tournament progress (based on number of players and expected matches)
            cur.execute(
                """
				WITH tournament_format AS (
				    SELECT
				        10 as round1_matches,
				        15 as round2_matches,
				        4 as knockout_matches,
				        10 + 15 + 4 as total_expected_matches, -- 29 total matches
				        25 as league_phase_matches -- round1 + round2
				),
				match_counts AS (
				    SELECT
				        COUNT(*) as matches_played,
				        COUNT(CASE WHEN match_type = '1v1' THEN 1 END) as matches_1v1_played,
				        COUNT(CASE WHEN match_type = '2v2' THEN 1 END) as matches_2v2_played
				    FROM matches
				    WHERE team1_goals IS NOT NULL
				    AND team2_goals IS NOT NULL
				)
				SELECT
				    m.matches_played,
				    t.total_expected_matches,
				    ROUND(
				        (m.matches_played::numeric / t.total_expected_matches::numeric * 100),
				        1
				    ) as completion_percentage,
				    CASE
				        WHEN m.matches_played < t.league_phase_matches THEN 'League Phase'
				        ELSE 'Knockout Phase'
				    END as current_phase,
				    CASE
				        WHEN m.matches_played < t.league_phase_matches THEN t.league_phase_matches
				        ELSE t.total_expected_matches
				    END as phase_total_matches,
				    CASE
				        WHEN m.matches_played < t.league_phase_matches THEN
				            ROUND((m.matches_played::numeric / t.league_phase_matches::numeric * 100), 1)
				        ELSE
				            ROUND(((m.matches_played - t.league_phase_matches)::numeric /
				                  (t.total_expected_matches - t.league_phase_matches)::numeric * 100), 1)
				    END as phase_completion_percentage
				FROM match_counts m
				CROSS JOIN tournament_format t;
            """
            )
            progress_stats = cur.fetchone()
            # progress_percentage = (
            #     (progress_stats["matches_played"] / progress_stats["total_expected_matches"] * 100)
            #     if progress_stats["total_expected_matches"] > 0
            #     else 0
            # )

            # Get basic tournament stats
            cur.execute(
                """
				SELECT
				    COUNT(*) as total_matches,
				    COALESCE(SUM(COALESCE(team1_goals, 0) + COALESCE(team2_goals, 0)), 0) as total_goals,
				    CASE
				        WHEN COUNT(*) > 0 THEN
				            ROUND(CAST(COALESCE(SUM(COALESCE(team1_goals, 0) + COALESCE(team2_goals, 0)), 0) AS NUMERIC) /
				            CAST(COUNT(*) AS NUMERIC), 2)
				        ELSE 0
				    END as avg_goals_per_match
				FROM matches
				WHERE team1_goals IS NOT NULL
				AND team2_goals IS NOT NULL;
			"""
            )
            basic_stats = cur.fetchone()

            # Get top scorer
            cur.execute(
                """
				WITH player_goals AS (
				    SELECT
				        p.player_id,
				        p.player_name,
				        COUNT(DISTINCT m.id) as matches_played,
				        SUM(
				            CASE
				                WHEN (m.team1_player1_id = p.player_id OR m.team1_player2_id = p.player_id) THEN m.team1_goals
				                WHEN (m.team2_player1_id = p.player_id OR m.team2_player2_id = p.player_id) THEN m.team2_goals
				                ELSE 0
				            END
				        ) as goals_scored,
				        json_agg(
				            json_build_object(
				                'match_date', to_char(m.match_date, 'YYYY-MM-DD'),
				                'match_type', m.match_type,
				                'goals_scored', (
				                    CASE
				                        WHEN (m.team1_player1_id = p.player_id OR
                                            m.team1_player2_id = p.player_id) THEN m.team1_goals
				                        WHEN (m.team2_player1_id = p.player_id OR
                                            m.team2_player2_id = p.player_id) THEN m.team2_goals
				                        ELSE 0
				                    END
				                ),
				                'opponent',
				                CASE
				                    WHEN (m.team1_player1_id = p.player_id OR m.team1_player2_id = p.player_id) THEN
				                        CASE
				                            WHEN m.match_type = '2v2' THEN
				                                CONCAT(p3.player_name, ' & ', p4.player_name)
				                            ELSE
				                                p3.player_name
				                        END
				                    ELSE
				                        CASE
				                            WHEN m.match_type = '2v2' THEN
				                                CONCAT(p1.player_name, ' & ', p2.player_name)
				                            ELSE
				                                p1.player_name
				                        END
				                END
				            ) ORDER BY m.match_date DESC
				        ) as match_details
				    FROM players p
				    JOIN matches m ON
				        p.player_id IN (
				            m.team1_player1_id, m.team1_player2_id,
				            m.team2_player1_id, m.team2_player2_id
				        )
				    LEFT JOIN players p1 ON m.team1_player1_id = p1.player_id
				    LEFT JOIN players p2 ON m.team1_player2_id = p2.player_id
				    LEFT JOIN players p3 ON m.team2_player1_id = p3.player_id
				    LEFT JOIN players p4 ON m.team2_player2_id = p4.player_id
				    WHERE m.team1_goals IS NOT NULL
				    AND m.team2_goals IS NOT NULL
				    GROUP BY p.player_id, p.player_name
				    HAVING SUM(
				        CASE
				            WHEN (m.team1_player1_id = p.player_id OR m.team1_player2_id = p.player_id) THEN m.team1_goals
				            WHEN (m.team2_player1_id = p.player_id OR m.team2_player2_id = p.player_id) THEN m.team2_goals
				            ELSE 0
				        END
				    ) > 0
				)
				SELECT
				    player_name,
				    goals_scored,
				    matches_played,
				    ROUND(CAST(goals_scored AS NUMERIC) / CAST(matches_played AS NUMERIC), 2) as goals_per_game,
				    match_details
				FROM player_goals
				ORDER BY
				    goals_scored DESC,
				    goals_per_game DESC,
				    matches_played ASC
				LIMIT 1;
			"""
            )
            top_scorer = cur.fetchone()

            # Get latest match
            cur.execute(
                """
				SELECT
				    m.*,
				    p1.player_name as team1_player1_name,
				    p2.player_name as team1_player2_name,
				    p3.player_name as team2_player1_name,
				    p4.player_name as team2_player2_name,
				    m.match_date,
				    CASE
				        WHEN m.match_type = '2v2' THEN
				            CONCAT(p1.player_name, ' & ', p2.player_name)
				        ELSE
				            p1.player_name
				    END as team1_display_name,
				    CASE
				        WHEN m.match_type = '2v2' THEN
				            CONCAT(p3.player_name, ' & ', p4.player_name)
				        ELSE
				            p3.player_name
				    END as team2_display_name
				FROM matches m
				LEFT JOIN players p1 ON m.team1_player1_id = p1.player_id
				LEFT JOIN players p2 ON m.team1_player2_id = p2.player_id
				LEFT JOIN players p3 ON m.team2_player1_id = p3.player_id
				LEFT JOIN players p4 ON m.team2_player2_id = p4.player_id
				WHERE m.team1_goals IS NOT NULL
				AND m.team2_goals IS NOT NULL
				ORDER BY m.match_date DESC
				LIMIT 1;
            """
            )
            latest_match = cur.fetchone()

            # Get highest scoring match
            cur.execute(
                """
			    SELECT
				    m.*,
				    p1.player_name as team1_player1_name,
				    p2.player_name as team1_player2_name,
				    p3.player_name as team2_player1_name,
				    p4.player_name as team2_player2_name,
				    COALESCE(team1_goals, 0) + COALESCE(team2_goals, 0) as total_goals
				FROM matches m
				LEFT JOIN players p1 ON m.team1_player1_id = p1.player_id
				LEFT JOIN players p2 ON m.team1_player2_id = p2.player_id
				LEFT JOIN players p3 ON m.team2_player1_id = p3.player_id
				LEFT JOIN players p4 ON m.team2_player2_id = p4.player_id
				WHERE team1_goals IS NOT NULL
				AND team2_goals IS NOT NULL
				ORDER BY
				    (COALESCE(team1_goals, 0) + COALESCE(team2_goals, 0)) DESC,
				    match_date DESC  -- Tiebreaker: most recent match
				LIMIT 1;
			"""
            )
            highest_scoring = cur.fetchone()

            # Get current winning streak
            cur.execute(
                """
				WITH match_results AS (
				    SELECT
				        id,
				        match_date,
				        match_type,
				        CASE
				            WHEN team1_goals > team2_goals THEN
				                ARRAY[team1_player1_id, team1_player2_id]
				            WHEN team2_goals > team1_goals THEN
				                ARRAY[team2_player1_id, team2_player2_id]
				            ELSE NULL
				        END as winner_ids,
				        team1_goals,
				        team2_goals
				    FROM matches
				    WHERE team1_goals IS NOT NULL AND team2_goals IS NOT NULL
				    ORDER BY match_date DESC
				),
				unnested_winners AS (
				    SELECT
				        id,
				        match_date,
				        match_type,
				        unnest(winner_ids) as player_id
				    FROM match_results
				    WHERE winner_ids IS NOT NULL
				),
				current_streaks AS (
				    SELECT
				        player_id,
				        COUNT(*) as streak_length
				    FROM (
				        SELECT
				            player_id,
				            match_date,
				            row_number() OVER (ORDER BY match_date DESC) -
				            row_number() OVER (PARTITION BY player_id ORDER BY match_date DESC) as grp
				        FROM unnested_winners
				        WHERE player_id IS NOT NULL
				    ) s
				    GROUP BY player_id, grp
				    ORDER BY streak_length DESC, grp
				    LIMIT 1
				),
				streak_matches AS (
				    SELECT
				        m.match_date,
				        m.match_type,
				        m.team1_goals,
				        m.team2_goals,
				        cs.player_id
				    FROM matches m
				    CROSS JOIN current_streaks cs
				    WHERE
				        (m.team1_goals > m.team2_goals AND
                            (m.team1_player1_id = cs.player_id OR
                                m.team1_player2_id = cs.player_id))
				        OR (m.team2_goals > m.team1_goals AND
                            (m.team2_player1_id = cs.player_id OR
                                m.team2_player2_id = cs.player_id))
				    ORDER BY m.match_date DESC
				    LIMIT (SELECT streak_length FROM current_streaks)
				)
				SELECT
				    p.player_name,
				    cs.streak_length as streak,
				    (SELECT match_date FROM streak_matches ORDER BY match_date DESC LIMIT 1) as last_match_date,
				    json_agg(
				        json_build_object(
				            'match_date', to_char(sm.match_date, 'YYYY-MM-DD'),
				            'match_type', sm.match_type,
				            'team1_goals', sm.team1_goals,
				            'team2_goals', sm.team2_goals
				        ) ORDER BY sm.match_date DESC
				    ) as streak_matches
				FROM current_streaks cs
				JOIN players p ON p.player_id = cs.player_id
				LEFT JOIN streak_matches sm ON sm.player_id = cs.player_id
				GROUP BY p.player_name, cs.streak_length;
            """
            )
            streak = cur.fetchone()

            # Get best defense stats
            cur.execute(
                """
				WITH player_matches AS (
				    SELECT
				        p.player_id,
				        p.player_name,
				        m.match_type,
				        m.match_date,
				        CASE
				            WHEN (m.team1_player1_id = p.player_id OR m.team1_player2_id = p.player_id) THEN m.team2_goals
				            WHEN (m.team2_player1_id = p.player_id OR m.team2_player2_id = p.player_id) THEN m.team1_goals
				        END as goals_conceded,
				        CASE
				            WHEN (m.team1_player1_id = p.player_id OR m.team1_player2_id = p.player_id) THEN
				                CASE
				                    WHEN m.match_type = '2v2' THEN
				                        CONCAT(p3.player_name, ' & ', p4.player_name)
				                    ELSE
				                        p3.player_name
				                END
				            ELSE
				                CASE
				                    WHEN m.match_type = '2v2' THEN
				                        CONCAT(p1.player_name, ' & ', p2.player_name)
				                    ELSE
				                        p1.player_name
				                END
				        END as opponent
				    FROM players p
				    JOIN matches m ON
				        p.player_id IN (
				            m.team1_player1_id, m.team1_player2_id,
				            m.team2_player1_id, m.team2_player2_id
				        )
				    LEFT JOIN players p1 ON m.team1_player1_id = p1.player_id
				    LEFT JOIN players p2 ON m.team1_player2_id = p2.player_id
				    LEFT JOIN players p3 ON m.team2_player1_id = p3.player_id
				    LEFT JOIN players p4 ON m.team2_player2_id = p4.player_id
				    WHERE m.team1_goals IS NOT NULL
				    AND m.team2_goals IS NOT NULL
				),
				defense_stats AS (
				    SELECT
				        player_id,
				        player_name,
				        COUNT(*) as matches_played,
				        SUM(goals_conceded) as goals_against,
				        ROUND(AVG(goals_conceded)::numeric, 2) as avg_conceded,
				        json_agg(
				            json_build_object(
				                'match_date', to_char(match_date, 'YYYY-MM-DD'),  -- Format date as string
				                'match_type', match_type,
				                'goals_conceded', goals_conceded,
				                'opponent', opponent
				            ) ORDER BY match_date DESC
				        ) as match_details
				    FROM player_matches
				    GROUP BY player_id, player_name
				    HAVING COUNT(*) >= 3  -- Minimum matches threshold to ensure fairness
				)
				SELECT
				    player_name,
				    goals_against,
				    matches_played,
				    avg_conceded as average,
				    match_details
				FROM defense_stats
				ORDER BY
				    goals_against ASC,  -- Primary sort: least goals conceded
				    matches_played DESC -- Secondary sort: more matches played (for ties)
				LIMIT 1;
			"""
            )
            best_defense = cur.fetchone()

            # Get clean sheets stats
            cur.execute(
                """
				WITH player_matches AS (
				    SELECT
				        p.player_id,
				        COUNT(*) as total_matches
				    FROM players p
				    JOIN matches m ON
				        (
				            m.team1_player1_id = p.player_id OR
				            m.team1_player2_id = p.player_id OR
				            m.team2_player1_id = p.player_id OR
				            m.team2_player2_id = p.player_id
				        )
				    WHERE m.team1_goals IS NOT NULL
				    AND m.team2_goals IS NOT NULL
				    GROUP BY p.player_id
				),
				player_clean_sheets AS (
				    SELECT
				        p.player_id,
				        p.player_name,
				        COUNT(*) as clean_sheet_count,
				        COUNT(*) * 100.0 / NULLIF(pm.total_matches, 0) as clean_sheet_percentage,
				        array_agg(
				            json_build_object(
				                'match_date', to_char(m.match_date, 'YYYY-MM-DD'),
				                'match_type', m.match_type,
				                'team1_goals', m.team1_goals,
				                'team2_goals', m.team2_goals,
				                'opponent', CASE
				                    WHEN (m.team1_player1_id = p.player_id OR m.team1_player2_id = p.player_id) THEN
				                        CASE
				                            WHEN m.match_type = '2v2' THEN
				                                CONCAT(po1.player_name, ' & ', po2.player_name)
				                            ELSE
				                                po1.player_name
				                        END
				                    ELSE
				                        CASE
				                            WHEN m.match_type = '2v2' THEN
				                                CONCAT(po3.player_name, ' & ', po4.player_name)
				                            ELSE
				                                po3.player_name
				                        END
				                END
				            ) ORDER BY m.match_date DESC
				        ) as clean_sheet_matches
				    FROM players p
				    JOIN matches m ON
				        (
				            (m.team1_player1_id = p.player_id OR m.team1_player2_id = p.player_id)
				            AND COALESCE(m.team2_goals, 0) = 0
				        ) OR
				        (
				            (m.team2_player1_id = p.player_id OR m.team2_player2_id = p.player_id)
				            AND COALESCE(m.team1_goals, 0) = 0
				        )
				    JOIN player_matches pm ON pm.player_id = p.player_id
				    -- Joins for opponent names
				    LEFT JOIN players po1 ON m.team2_player1_id = po1.player_id
				    LEFT JOIN players po2 ON m.team2_player2_id = po2.player_id
				    LEFT JOIN players po3 ON m.team1_player1_id = po3.player_id
				    LEFT JOIN players po4 ON m.team1_player2_id = po4.player_id
				    WHERE m.team1_goals IS NOT NULL
				    AND m.team2_goals IS NOT NULL
				    GROUP BY p.player_id, p.player_name, pm.total_matches
				    HAVING COUNT(*) > 0
				    ORDER BY clean_sheet_count DESC, clean_sheet_percentage DESC
				    LIMIT 5
				)
				SELECT
				    player_name,
				    clean_sheet_count as count,
				    clean_sheet_percentage as percentage,
				    clean_sheet_matches as matches_detail
				FROM player_clean_sheets;
			"""
            )
            clean_sheets_data = cur.fetchone()

            return {
                "progress": {
                    "percentage": progress_stats["completion_percentage"],
                    "matchesPlayed": progress_stats["matches_played"],
                    "totalMatches": progress_stats["total_expected_matches"],
                    "currentPhase": progress_stats["current_phase"],
                    "phasePercentage": progress_stats["phase_completion_percentage"],
                    "phaseTotalMatches": progress_stats["phase_total_matches"],
                }
                if progress_stats
                else {
                    "percentage": 0,
                    "matchesPlayed": 0,
                    "totalMatches": 29,
                    "currentPhase": "League Phase",
                    "phasePercentage": 0,
                    "phaseTotalMatches": 25,
                },
                "stats": {
                    "totalMatches": basic_stats["total_matches"],
                    "totalGoals": basic_stats["total_goals"],
                    "averageGoals": float(basic_stats["avg_goals_per_match"]),
                }
                if basic_stats
                else {"totalMatches": 0, "totalGoals": 0, "averageGoals": 0},
                "topScorer": {
                    "name": top_scorer["player_name"],
                    "goals": top_scorer["goals_scored"],
                    "matches": top_scorer["matches_played"],
                    "average": float(top_scorer["goals_per_game"]),
                    "details": top_scorer["match_details"] if top_scorer and top_scorer["match_details"] else [],
                }
                if top_scorer
                else None,
                "latestMatch": {
                    "team1": latest_match["team1_display_name"],
                    "team2": latest_match["team2_display_name"],
                    "score1": latest_match["team1_goals"] or 0,
                    "score2": latest_match["team2_goals"] or 0,
                    "date": latest_match["match_date"].strftime("%Y-%m-%d %H:%M"),
                    "matchType": latest_match["match_type"],
                    # Additional useful information
                    "isComplete": latest_match["team1_goals"] is not None and latest_match["team2_goals"] is not None,
                }
                if latest_match
                else None,
                "highestScoring": {
                    "team1": (
                        f"{highest_scoring['team1_player1_name']} & {highest_scoring['team1_player2_name']}"
                        if highest_scoring["team1_player2_name"]
                        else highest_scoring["team1_player1_name"]
                    ),
                    "team2": (
                        f"{highest_scoring['team2_player1_name']} & {highest_scoring['team2_player2_name']}"
                        if highest_scoring["team2_player2_name"]
                        else highest_scoring["team2_player1_name"]
                    ),
                    "score1": highest_scoring["team1_goals"] or 0,
                    "score2": highest_scoring["team2_goals"] or 0,
                    "totalGoals": highest_scoring["total_goals"] or 0,
                    "date": highest_scoring["match_date"].strftime("%Y-%m-%d"),
                    "matchType": highest_scoring["match_type"],
                }
                if highest_scoring and highest_scoring["team1_goals"] is not None
                else None,
                "currentStreak": {
                    "player": streak["player_name"] if streak else None,
                    "wins": streak["streak"] if streak else 0,
                    "matchType": "1v1/2v2",  # Added to show what types of matches made up the streak
                    # Use the separate last_match_date field which is still a datetime
                    "lastMatch": streak["last_match_date"].strftime("%Y-%m-%d")
                    if streak and streak["last_match_date"]
                    else None,
                }
                if streak
                else None,
                "bestDefense": {
                    "player": best_defense["player_name"],
                    "goalsAgainst": best_defense["goals_against"],
                    "average": float(best_defense["average"]),
                    "matches": best_defense["matches_played"],
                    "details": best_defense["match_details"] if best_defense and best_defense["match_details"] else [],
                }
                if best_defense
                else None,
                "cleanSheets": {
                    "player": clean_sheets_data["player_name"],
                    "count": clean_sheets_data["count"] or 0,
                    "percentage": round(clean_sheets_data["percentage"] or 0, 1),
                    "matches": [
                        {
                            "date": match["match_date"],  # Already formatted in SQL
                            "opponent": match["opponent"],
                            "matchType": match["match_type"],
                        }
                        for match in clean_sheets_data["matches_detail"]
                    ]
                    if clean_sheets_data and clean_sheets_data["matches_detail"]
                    else [],
                }
                if clean_sheets_data
                else None,
            }
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        print(f"Error in get_overview_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
