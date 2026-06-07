# Module: app.models.currency
# Description: SQLAlchemy database model defining forex rates and commodity indices.

from datetime import datetime
from sqlalchemy import Column, Float, DateTime, String, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base


class CurrencyData(Base):
    __tablename__ = "currency_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recording_date = Column(DateTime, unique=True, nullable=False, index=True)
    usd_inr = Column(Float, nullable=False)
    bytes_inr = Column(Float, nullable=True) # Unused field, placeholder
    eur_usd = Column(Float, nullable=False)
    brent_crude = Column(Float, nullable=False)
    gold_index = Column(Float, nullable=False)
    
    # Exogenous Benchmarks & Score Signals (Phase 9 additions)
    dxy_index = Column(Float, nullable=True)
    vix_index = Column(Float, nullable=True)
    usd_inr_trend_score = Column(Float, nullable=True)
    usd_inr_risk_score = Column(Float, nullable=True)
    brent_crude_shock_score = Column(Float, nullable=True)
    inflation_impact_score = Column(Float, nullable=True)


class CurrencyForecast(Base):
    __tablename__ = "currency_forecasts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_asset = Column(String, nullable=False, index=True) # e.g. "USD/INR", "Brent Crude"
    horizon_days = Column(Integer, nullable=False, index=True) # 30, 60, 90, 180, 365
    forecast_date = Column(DateTime, nullable=False)
    projected_value = Column(Float, nullable=False)
    confidence_upper = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

