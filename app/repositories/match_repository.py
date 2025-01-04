from typing import Optional

from database import get_connection
from models import MatchCreate
from psycopg2.extras import RealDictCursor


class MatchRepository:
    async def get_matches(self):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(
                """
                SELECT m.*,
                       p1.player_name as team1_player1_name,
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
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    async def get_match_by_id(self, match_id: int):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute("SELECT * FROM matches WHERE id = %s", (match_id,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    async def create_match(self, match: MatchCreate, scheduled_date, status: str, result: Optional[str]):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            # Validate players exist
            player_ids = [match.team1_player1_id, match.team2_player1_id]
            if match.match_type == "2v2":
                player_ids.extend([match.team1_player2_id, match.team2_player2_id])

            cur.execute("SELECT player_id FROM players WHERE player_id = ANY(%s)", (player_ids,))
            found_players = cur.fetchall()
            if len(found_players) != len(set(player_ids)):
                raise ValueError("One or more players not found in database")

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
            conn.commit()
            return new_match
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()

    async def update_match(self, match_id: int, match: MatchCreate, status: str, result: Optional[str]):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
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
                    match.team1_goals,
                    match.team2_goals,
                    status,
                    result,
                    match_id,
                ),
            )

            updated_match = cur.fetchone()
            conn.commit()
            return updated_match
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()

    async def update_match_score(self, match_id: int, team1_goals: int, team2_goals: int, result: str):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
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
            conn.commit()
            return updated_match
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()

    async def delete_match(self, match_id: int):
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute("DELETE FROM matches WHERE id = %s RETURNING *", (match_id,))
            deleted_match = cur.fetchone()
            conn.commit()
            return deleted_match
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
