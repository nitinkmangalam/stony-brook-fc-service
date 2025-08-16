from typing import List

from fastapi import HTTPException

from app.models import Player, PlayerCreate
from app.repositories.player_repository import PlayerRepository


class PlayerService:
    def __init__(self):
        self.repository = PlayerRepository()

    def get_all_players(self) -> List[Player]:
        try:
            players = self.repository.get_all_players()
            return [Player(**player) for player in players]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching players: {str(e)}")

    def create_player(self, player: PlayerCreate) -> Player:
        try:
            # Additional business logic can be added here
            # For example, validating player name format, checking for duplicates, etc.
            new_player = self.repository.create_player(player)
            return Player(**new_player)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error creating player: {str(e)}")

    def get_player_by_id(self, player_id: int) -> Player:
        player = self.repository.get_player_by_id(player_id)
        if not player:
            raise HTTPException(status_code=404, detail=f"Player with ID {player_id} not found")
        return Player(**player)

    def delete_player(self, player_id: int) -> Player:
        try:
            deleted_player = self.repository.delete_player(player_id)
            if not deleted_player:
                raise HTTPException(status_code=404, detail=f"Player with ID {player_id} not found")
            return Player(**deleted_player)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting player: {str(e)}")
