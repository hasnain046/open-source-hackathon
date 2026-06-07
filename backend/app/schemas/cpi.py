# Module: app.schemas.cpi
# Description: Pydantic schemas defining CPI categories weights and item breakdowns returns.

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel
from uuid import UUID


class InflationSummarySchema(BaseModel):
    id: UUID
    reporting_date: datetime
    headline_rate: float
    core_rate: float
    wholesale_rate: float

    class Config:
        from_attributes = True


class CPICategoryResponseSchema(BaseModel):
    id: UUID
    inflation_id: UUID
    category_name: str
    weight: float
    current_rate: float
    sub_items: Optional[List[Dict]] = None

    class Config:
        from_attributes = True
