# Module: app.schemas.trends
# Description: Pydantic schemas defining historical inflation and comparison trends.

from pydantic import BaseModel


class HistoricalTrendResponseSchema(BaseModel):
    year: str
    rate: float
    growth: float


class DetailedTrendResponseSchema(BaseModel):
    date: str
    inflation: float
    food: float
    fuel: float
    core: float
