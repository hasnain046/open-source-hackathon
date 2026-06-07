# Module: app.api.v1.admin
# Description: Router handling system diagnostics, database audits, and background tasks logs.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, RoleChecker
from app.services.admin_service import AdminService
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["System Administration"])


@router.get("/stats", dependencies=[Depends(RoleChecker(["admin"]))])
def get_system_stats(db: Session = Depends(get_db)):
    """Retrieve operational database metrics and worker jobs status (Admin only)."""
    return AdminService.get_system_stats(db)


@router.get("/system-health", dependencies=[Depends(RoleChecker(["admin"]))])
def get_system_health(db: Session = Depends(get_db)):
    """Perform system checks on DB connection and background workers (Admin only)."""
    return AdminService.get_system_health(db)
