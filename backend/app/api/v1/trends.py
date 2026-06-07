# Module: app.api.v1.trends
# Description: Router handling historical inflation trends and sector comparison timelines.

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.trends import HistoricalTrendResponseSchema, DetailedTrendResponseSchema
from app.services.trends_service import TrendsService

router = APIRouter(prefix="/trends", tags=["Historical Trends"])


@router.get("/history", response_model=List[HistoricalTrendResponseSchema])
def get_historical_trends(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve annual headline inflation rate averages and growths."""
    return TrendsService.get_historical_trends(db)


@router.get("/comparison", response_model=List[DetailedTrendResponseSchema])
def get_comparison_trends(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve detailed month-over-month subsector inflation trends overlays."""
    return TrendsService.get_comparison_trends(db)
