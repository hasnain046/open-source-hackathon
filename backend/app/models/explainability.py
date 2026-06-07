# Module: app.models.explainability
# Description: SQLAlchemy database model defining local SHAP explainability variables.

from datetime import datetime
from sqlalchemy import Column, Float, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base


class ForecastExplainability(Base):
    __tablename__ = "forecast_explainability"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    forecast_date = Column(DateTime, nullable=False, index=True)
    model_type = Column(String, nullable=False, index=True)
    base_value = Column(Float, nullable=False)
    prediction_value = Column(Float, nullable=False)
    cpi_momentum_contribution = Column(Float, nullable=False)
    commodity_shock_contribution = Column(Float, nullable=False)
    currency_exchange_contribution = Column(Float, nullable=False)
    risk_sentiment_contribution = Column(Float, nullable=False)
    monetary_policy_contribution = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    confidence_indicator = Column(String, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
