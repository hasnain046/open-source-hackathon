# Module: app.schemas.news
# Description: Pydantic schemas defining parsed financial news headlines and sentiment ratings outputs.

from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel
from uuid import UUID


class NewsItemResponseSchema(BaseModel):
    id: UUID
    headline: str
    source: str
    url: Optional[str] = None
    category: str
    sentiment: str
    impact_score: float
    published_at: datetime

    class Config:
        from_attributes = True


class NewsSentimentResponseSchema(BaseModel):
    average_impact_score: float
    sentiment_counts: Dict[str, int]
    sentiment_score: Optional[float] = None
    economic_risk_score: Optional[float] = None
    inflation_pressure_score: Optional[float] = None
    topic_trends: Optional[Dict[str, float]] = None
    regional_impact: Optional[Dict[str, int]] = None
