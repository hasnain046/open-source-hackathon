# Module: app.schemas.heatmap
# Description: Pydantic schemas defining state-wise regional consumer price rates response layouts.

from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class HeatmapStateResponseSchema(BaseModel):
    id: UUID
    state_name: str
    region: str
    current_rate: float
    year_ago_rate: float
    threat_level: str
    updated_at: datetime

    class Config:
        from_attributes = True
