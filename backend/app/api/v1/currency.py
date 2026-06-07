# Module: app.api.v1.currency
# Description: Router handling exchange rates data overlays and commodity indices.

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.currency import ForexResponseSchema, CommodityResponseSchema, CurrencyPredictionResponseSchema, CurrencyImpactScoresResponseSchema
from app.services.currency_service import CurrencyService

router = APIRouter(prefix="/currency", tags=["Forex & Commodities"])


@router.get("/forex", response_model=List[ForexResponseSchema])
def get_forex_rates(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve USD/INR and EUR/USD forex exchange conversion rates overlays."""
    return CurrencyService.get_forex_rates(db)


@router.get("/commodities", response_model=List[CommodityResponseSchema])
def get_commodity_indices(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve historical Brent Crude and Gold spot commodity price index benchmarks."""
    return CurrencyService.get_commodity_rates(db)


@router.get("/predictions", response_model=List[CurrencyPredictionResponseSchema])
def get_currency_predictions(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve LSTM exchange rate and commodity projections for aligned horizons (30, 60, 90, 180, 365 Days)."""
    return CurrencyService.get_currency_predictions(db)


@router.get("/impact-scores", response_model=CurrencyImpactScoresResponseSchema)
def get_currency_impact_scores(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve aggregate currency trend scores, currency risk scores, commodity shocks, and inflation impacts."""
    return CurrencyService.get_currency_impact_scores(db)
