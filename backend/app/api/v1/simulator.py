# Module: app.api.v1.simulator
# Description: Router handling policy slider shock variables and projected impact outputs.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.simulation import RunSimulationSchema, SimulationResponseSchema
from app.services.simulator_service import SimulatorService
from app.models.user import User

router = APIRouter(prefix="/simulator", tags=["Scenario Simulator"])


@router.post("/run", response_model=SimulationResponseSchema)
def run_shock_simulation(
    params: RunSimulationSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculate projected CPI deviation based on input sliders."""
    return SimulatorService.run_shock_simulation(current_user.id, params, db)
