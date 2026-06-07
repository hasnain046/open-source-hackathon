# Module: app.models.cpi
# Description: SQLAlchemy database models defining aggregate inflation entries and cpi basket structures.

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class InflationData(Base):
    __tablename__ = "inflation_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporting_date = Column(DateTime, unique=True, nullable=False, index=True)
    headline_rate = Column(Float, nullable=False)
    core_rate = Column(Float, nullable=False)
    wholesale_rate = Column(Float, nullable=False)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    # ORM Relationships
    cpi_entries = relationship("CPIData", back_populates="inflation", cascade="all, delete-orphan")


class CPIData(Base):
    __tablename__ = "cpi_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inflation_id = Column(UUID(as_uuid=True), ForeignKey("inflation_data.id"), nullable=False, index=True)
    category_name = Column(String, nullable=False, index=True)
    weight = Column(Float, nullable=False)
    current_rate = Column(Float, nullable=False)
    sub_items = Column(JSONB, nullable=True)

    # ORM Relationships
    inflation = relationship("InflationData", back_populates="cpi_entries")
