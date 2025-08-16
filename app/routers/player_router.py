from typing import List

from fastapi import APIRouter, Depends
from models import Player, PlayerCreate

from app.services.player_service import PlayerService

router = APIRouter(prefix="/players", tags=["players"])


def get_player_service():
    return PlayerService()


@router.get("", response_model=List[Player])
async def get_players(player_service: PlayerService = Depends(get_player_service)):
    return player_service.get_all_players()


@router.post("", response_model=Player)
async def create_player(player: PlayerCreate, player_service: PlayerService = Depends(get_player_service)):
    return player_service.create_player(player)


@router.get("/{player_id}", response_model=Player)
async def get_player(player_id: int, player_service: PlayerService = Depends(get_player_service)):
    return player_service.get_player_by_id(player_id)


@router.delete("/{player_id}", response_model=Player)
async def delete_player(player_id: int, player_service: PlayerService = Depends(get_player_service)):
    return player_service.delete_player(player_id)
