# Module: app.schemas.simulation
# Description: Pydantic schemas defining simulator sliders variables and simulation responses.

from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class RunSimulationSchema(BaseModel):
    oil_change: float = Field(..., description="Landed crude oil price deviation ($/bbl)")
    interest_rate_change: float = Field(..., description="Monetary policy repo rate deviation in bps")
    currency_change: float = Field(..., description="Local exchange strength change percentage")


class SimulationResponseSchema(BaseModel):
    id: UUID
    user_id: UUID | None = None
    input_crude_change: float
    input_rate_change: float
    input_currency_change: float
    output_projected_rate: float
    executed_at: datetime

    class Config:
        from_attributes = True
