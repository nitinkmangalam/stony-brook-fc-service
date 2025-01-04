from fastapi import APIRouter, HTTPException
from services.standing_service import StandingService

router = APIRouter(prefix="/standings", tags=["standings"])


@router.get("")
async def get_standings():
    try:
        service = StandingService()
        return await service.get_standings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
