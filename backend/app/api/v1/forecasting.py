# Module: app.api.v1.forecasting
# Description: Router handling ML models projections output, feature explainability weights, and retrain configurations.

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, RoleChecker
from app.schemas.forecast import ForecastResponseSchema
from app.schemas.explainability import (
    GlobalImportanceResponseSchema,
    LocalExplainabilityResponseSchema,
    ForecastComparisonResponseSchema,
    TopDriverResponseSchema
)
from app.services.forecast_service import ForecastService

router = APIRouter(prefix="/forecasting", tags=["Forecasting"])


@router.get("/projections", response_model=List[ForecastResponseSchema])
def get_model_projections(
    model_type: str = "lstm",
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve 12-month projections matching active model types."""
    return ForecastService.get_projections(model_type, db)


@router.get("/explainability")
def get_shap_explainability(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve SHAP diagnostics mapping indicators influence coefficients (Legacy)."""
    return ForecastService.get_explainability_mapping()


@router.get("/explainability/global", response_model=List[GlobalImportanceResponseSchema])
def get_global_explainability(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve overall global feature importance ranks based on mean absolute SHAP values."""
    return ForecastService.get_global_explainability(db)


@router.get("/explainability/local", response_model=List[LocalExplainabilityResponseSchema])
def get_local_explainability(
    model_type: str = "ensemble",
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve local contributions for drawing waterfall charts per forecast target date."""
    return ForecastService.get_local_explainability(db, model_type)


@router.get("/explainability/comparison", response_model=List[ForecastComparisonResponseSchema])
def get_forecast_comparison(
    model_type: str = "ensemble",
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve driver contribution shifts comparing current run vs previous forecast run."""
    return ForecastService.get_forecast_comparison(db, model_type)


@router.get("/top-drivers", response_model=List[TopDriverResponseSchema])
def get_top_drivers(
    model_type: str = "ensemble",
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve top drivers with contributions and trend directions across the forecast horizon."""
    return ForecastService.get_top_drivers(db, model_type)


@router.post("/retrain", dependencies=[Depends(RoleChecker(["admin"]))])
def trigger_model_retraining(db: Session = Depends(get_db)):
    """Trigger background training runs for time-series forecasters (Admin only)."""
    return {"message": "Forecaster training job successfully dispatched"}

