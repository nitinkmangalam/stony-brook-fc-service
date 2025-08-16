from typing import List

from fastapi import APIRouter, Depends

from app.models import Match, MatchCreate, ScoreUpdate
from app.services.match_service import MatchService

router = APIRouter(prefix="/matches", tags=["matches"])


def get_match_service():
    return MatchService()


@router.get("", response_model=List[Match])
async def get_matches(match_service: MatchService = Depends(get_match_service)):
    return await match_service.get_matches()


@router.post("", response_model=Match)
async def create_match(match: MatchCreate, match_service: MatchService = Depends(get_match_service)):
    return await match_service.create_match(match)


@router.get("/{match_id}", response_model=Match)
async def get_match(match_id: int, match_service: MatchService = Depends(get_match_service)):
    return await match_service.get_match_by_id(match_id)


@router.put("/{match_id}", response_model=Match)
async def update_match(match_id: int, match: MatchCreate, match_service: MatchService = Depends(get_match_service)):
    return await match_service.update_match(match_id, match)


@router.put("/{match_id}/score", response_model=Match)
async def update_match_score(
    match_id: int, score: ScoreUpdate, match_service: MatchService = Depends(get_match_service)
):
    return await match_service.update_match_score(match_id, score)


@router.delete("/{match_id}", response_model=Match)
async def delete_match(match_id: int, match_service: MatchService = Depends(get_match_service)):
    return await match_service.delete_match(match_id)
