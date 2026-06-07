# Module: app.api.v1.heatmap
# Description: Router handling state-wise regional consumer price rates mapping.

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.heatmap import HeatmapStateResponseSchema
from app.services.heatmap_service import HeatmapService

router = APIRouter(prefix="/heatmap", tags=["Regional Heatmap"])


@router.get("/states", response_model=List[HeatmapStateResponseSchema])
def get_states_heatmap(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve consumer prices mapping parameters sorted by state."""
    return HeatmapService.get_state_metrics(db)
