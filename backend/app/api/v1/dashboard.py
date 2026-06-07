# Module: app.api.v1.dashboard
# Description: Router handling aggregate dashboard indicators summary.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.dashboard import DashboardSummaryResponseSchema
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponseSchema)
def get_dashboard_summary(
    current_user: str = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Aggregate primary KPIs and news digests for frontpage dashboards."""
    return DashboardService.get_summary(db)
