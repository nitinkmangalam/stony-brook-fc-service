from typing import Dict, List

from psycopg2.extras import RealDictCursor

from app.database import get_connection


class StandingRepository:
    async def get_round1_standings(self) -> List[Dict]:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(
                """
                WITH round1_stats AS (
                    SELECT
                        p.player_id,
                        p.player_name,
                        COUNT(*) as matches_played,
                        SUM(CASE
                            WHEN (m.team1_player1_id = p.player_id AND
                                    COALESCE(m.team1_goals, 0) > COALESCE(m.team2_goals, 0)) OR
                                 (m.team2_player1_id = p.player_id AND
                                    COALESCE(m.team2_goals, 0) > COALESCE(m.team1_goals, 0)) THEN 1
                            ELSE 0
                        END) as wins,
                        SUM(CASE
                            WHEN COALESCE(m.team1_goals, 0) = COALESCE(m.team2_goals, 0) THEN 1
                            ELSE 0
                        END) as draws,
                        SUM(CASE
                            WHEN (m.team1_player1_id = p.player_id AND
                                    COALESCE(m.team1_goals, 0) < COALESCE(m.team2_goals, 0)) OR
                                 (m.team2_player1_id = p.player_id AND
                                    COALESCE(m.team2_goals, 0) < COALESCE(m.team1_goals, 0)) THEN 1
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
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    async def get_round2_standings(self) -> List[Dict]:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
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
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()
