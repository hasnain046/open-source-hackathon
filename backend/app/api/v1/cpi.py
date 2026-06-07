# Module: app.api.v1.cpi
# Description: Router handling Consumer Price Index category weights and items breakdowns.

from typing import List, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.cpi import CPICategoryResponseSchema
from app.services.cpi_service import CPIService

router = APIRouter(prefix="/cpi", tags=["CPI Basket"])


@router.get("/categories", response_model=List[CPICategoryResponseSchema])
def get_cpi_categories(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve weights and rates for principal CPI sectors."""
    return CPIService.get_categories(db)


@router.get("/subcategories/{id}", response_model=List[Dict])
def get_cpi_subcategories(
    id: str,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve itemized subcategories list metrics."""
    return CPIService.get_subcategory(id, db)
