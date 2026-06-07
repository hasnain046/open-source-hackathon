# Module: app.schemas.currency
# Description: Pydantic schemas defining forex and commodity indices response layouts.

from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class ForexResponseSchema(BaseModel):
    id: UUID
    recording_date: datetime
    usd_inr: float
    eur_usd: float

    class Config:
        from_attributes = True


class CommodityResponseSchema(BaseModel):
    id: UUID
    recording_date: datetime
    brent_crude: float
    gold_index: float

    class Config:
        from_attributes = True


class CurrencyPredictionResponseSchema(BaseModel):
    id: UUID
    target_asset: str
    horizon_days: int
    forecast_date: datetime
    projected_value: float
    confidence_upper: float
    confidence_lower: float
    generated_at: datetime

    class Config:
        from_attributes = True


class CurrencyImpactScoresResponseSchema(BaseModel):
    currency_trend_score: float
    currency_risk_score: float
    commodity_shock_score: float
    inflation_impact_score: float
    recording_date: datetime

    class Config:
        from_attributes = True
