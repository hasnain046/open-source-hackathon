# Module: app.schemas.explainability
# Description: Pydantic validation schemas for SHAP explainability dashboard responses.

from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional


class GlobalImportanceResponseSchema(BaseModel):
    feature_name: str
    category: str
    importance_value: float
    confidence_score: float
    confidence_indicator: str

    class Config:
        from_attributes = True


class LocalExplainabilityResponseSchema(BaseModel):
    id: UUID
    forecast_date: datetime
    model_type: str
    base_value: float
    prediction_value: float
    cpi_momentum_contribution: float
    commodity_shock_contribution: float
    currency_exchange_contribution: float
    risk_sentiment_contribution: float
    monetary_policy_contribution: float
    confidence_score: float
    confidence_indicator: str
    generated_at: datetime

    class Config:
        from_attributes = True


class ForecastComparisonResponseSchema(BaseModel):
    forecast_date: datetime
    previous_prediction: float
    current_prediction: float
    prediction_change: float
    cpi_momentum_change: float
    commodity_shock_change: float
    currency_exchange_change: float
    risk_sentiment_change: float
    monetary_policy_change: float
    confidence_score: float
    confidence_indicator: str

    class Config:
        from_attributes = True


class TopDriverResponseSchema(BaseModel):
    driver_name: str
    contribution: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    confidence_score: float
    confidence_indicator: str

    class Config:
        from_attributes = True
