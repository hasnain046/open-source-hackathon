# Module: app.schemas.dashboard
# Description: Pydantic schemas defining aggregate dashboard KPIs summary.

from typing import Dict, List
from pydantic import BaseModel
from app.schemas.news import NewsItemResponseSchema
from app.schemas.cpi import CPICategoryResponseSchema


class CurrentInflationSchema(BaseModel):
    rate: float
    changePrevMonth: float
    targetRate: float
    confidenceInterval: List[float]
    lastUpdated: str
    quickStats: Dict[str, float]


class ForecastSnapshotSchema(BaseModel):
    lstmForecastNextMonth: float
    prophetForecastNextMonth: float
    confidenceScore: float
    direction: str
    dominantDriver: str


class CurrencySnapshotSchema(BaseModel):
    usd_inr: float
    brent_crude: float
    eur_usd: float
    gold_index: float


class DashboardSummaryResponseSchema(BaseModel):
    current_inflation: CurrentInflationSchema
    cpi_summary: List[CPICategoryResponseSchema]
    forecast_snapshot: ForecastSnapshotSchema
    news_summary: List[NewsItemResponseSchema]
    currency_snapshot: CurrencySnapshotSchema
