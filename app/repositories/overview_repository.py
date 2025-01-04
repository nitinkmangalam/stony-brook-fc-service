from typing import Dict, Optional

from database import get_connection
from psycopg2.extras import RealDictCursor


class OverviewRepository:
    def get_tournament_progress(self) -> Optional[Dict]:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(
                """
                WITH tournament_format AS (
                    SELECT
                        10 as round1_matches,
                        15 as round2_matches,
                        4 as knockout_matches,
                        10 + 15 + 4 as total_expected_matches,
                        25 as league_phase_matches
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
                CROSS JOIN tournament_format t
            """
            )
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def get_basic_tournament_stats(self) -> Optional[Dict]:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(
                """
                SELECT
                    COUNT(*) as total_matches,
                    COALESCE(SUM(COALESCE(team1_goals, 0) + COALESCE(team2_goals, 0)), 0) as total_goals,
                    CASE
                        WHEN COUNT(*) > 0 THEN
                            ROUND(CAST(COALESCE(
                                    SUM(COALESCE(team1_goals, 0) + COALESCE(team2_goals, 0)),
                                    0
                                ) AS NUMERIC) /
                            CAST(COUNT(*) AS NUMERIC), 2)
                        ELSE 0
                    END as avg_goals_per_match
                FROM matches
                WHERE team1_goals IS NOT NULL
                AND team2_goals IS NOT NULL
            """
            )
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def get_top_scorer(self) -> Optional[Dict]:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(
                """
                WITH player_goals AS (
                    SELECT
                        p.player_id,
                        p.player_name,
                        COUNT(DISTINCT m.id) as matches_played,
                        SUM(
                            CASE
                                WHEN (m.team1_player1_id = p.player_id OR
                                    m.team1_player2_id = p.player_id) THEN m.team1_goals
                                WHEN (m.team2_player1_id = p.player_id OR
                                    m.team2_player2_id = p.player_id) THEN m.team2_goals
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
                                    WHEN (m.team1_player1_id = p.player_id OR
                                        m.team1_player2_id = p.player_id) THEN
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
                            WHEN (m.team1_player1_id = p.player_id OR
                                m.team1_player2_id = p.player_id) THEN m.team1_goals
                            WHEN (m.team2_player1_id = p.player_id OR
                                m.team2_player2_id = p.player_id) THEN m.team2_goals
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
                LIMIT 1
            """
            )
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def get_latest_match(self) -> Optional[Dict]:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
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
                LIMIT 1
            """
            )
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def get_highest_scoring_match(self) -> Optional[Dict]:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
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
                    match_date DESC
                LIMIT 1
            """
            )
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def get_current_streak(self) -> Optional[Dict]:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
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
                GROUP BY p.player_name, cs.streak_length
            """
            )
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def get_best_defense(self) -> Optional[Dict]:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(
                """
                WITH player_matches AS (
                    SELECT
                        p.player_id,
                        p.player_name,
                        m.match_type,
                        m.match_date,
                        CASE
                            WHEN (m.team1_player1_id = p.player_id OR
                                m.team1_player2_id = p.player_id) THEN m.team2_goals
                            WHEN (m.team2_player1_id = p.player_id OR
                                m.team2_player2_id = p.player_id) THEN m.team1_goals
                        END as goals_conceded,
                        CASE
                            WHEN (m.team1_player1_id = p.player_id OR
                                m.team1_player2_id = p.player_id) THEN
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
                                'match_date', to_char(match_date, 'YYYY-MM-DD'),
                                'match_type', match_type,
                                'goals_conceded', goals_conceded,
                                'opponent', opponent
                            ) ORDER BY match_date DESC
                        ) as match_details
                    FROM player_matches
                    GROUP BY player_id, player_name
                    HAVING COUNT(*) >= 3
                )
                SELECT
                    player_name,
                    goals_against,
                    matches_played,
                    avg_conceded as average,
                    match_details
                FROM defense_stats
                ORDER BY
                    goals_against ASC,
                    matches_played DESC
                LIMIT 1
            """
            )
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def get_clean_sheets(self) -> Optional[Dict]:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
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
                FROM player_clean_sheets
            """
            )
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()
