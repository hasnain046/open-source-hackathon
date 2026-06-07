# Module: app.schemas.forecast
# Description: Pydantic schemas defining ML forecaster output values and accuracy diagnostics returns.

from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel
from uuid import UUID


class ForecastResponseSchema(BaseModel):
    id: UUID
    model_type: str
    target_date: datetime
    projected_rate: float
    confidence_upper: float
    confidence_lower: float
    shap_contributions: Optional[Dict[str, float]] = None
    generated_at: datetime

    class Config:
        from_attributes = True
