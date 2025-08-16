from typing import List, Optional

from psycopg2.extras import RealDictCursor

from app.database import get_connection
from app.models import PlayerCreate


class PlayerRepository:
    def get_all_players(self) -> List[dict]:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(
                """
                SELECT * FROM players
                ORDER BY player_name
            """
            )
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    def create_player(self, player: PlayerCreate) -> dict:
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
            raise e
        finally:
            cur.close()
            conn.close()

    def get_player_by_id(self, player_id: int) -> Optional[dict]:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(
                """
                SELECT * FROM players
                WHERE player_id = %s
                """,
                (player_id,),
            )
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def delete_player(self, player_id: int) -> Optional[dict]:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            # First check if player exists
            cur.execute(
                """
                SELECT * FROM players
                WHERE player_id = %s
                """,
                (player_id,),
            )
            player = cur.fetchone()
            if not player:
                return None

            # Check if player has any matches
            cur.execute(
                """
                SELECT COUNT(*) FROM matches
                WHERE team1_player1_id = %s
                   OR team1_player2_id = %s
                   OR team2_player1_id = %s
                   OR team2_player2_id = %s
                """,
                (player_id, player_id, player_id, player_id),
            )
            match_count = cur.fetchone()["count"]
            if match_count > 0:
                raise ValueError(
                    f"Cannot delete player with ID {player_id} as they have {match_count} matches associated"
                )

            # Delete the player if no matches found
            cur.execute(
                """
                DELETE FROM players
                WHERE player_id = %s
                RETURNING *
                """,
                (player_id,),
            )
            deleted_player = cur.fetchone()
            conn.commit()
            return deleted_player
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
