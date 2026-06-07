# Module: app.models.forecast
# Description: SQLAlchemy database model defining the machine learning model forecast entities.

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    base_inflation_id = Column(UUID(as_uuid=True), ForeignKey("inflation_data.id"), nullable=True, index=True)
    model_type = Column(String, nullable=False, index=True)
    target_date = Column(DateTime, nullable=False)
    projected_rate = Column(Float, nullable=False)
    confidence_upper = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=False)
    shap_contributions = Column(JSONB, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    # ORM Relationships
    base_inflation = relationship("InflationData")
