from typing import Dict

from fastapi import APIRouter, Depends

from app.services.overview_service import OverviewService

router = APIRouter(prefix="/overview", tags=["overview"])


def get_overview_service():
    return OverviewService()


@router.get("", response_model=Dict)
async def get_overview_stats(overview_service: OverviewService = Depends(get_overview_service)):
    return overview_service.get_overview_stats()
