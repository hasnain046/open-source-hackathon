# Module: app.models.heatmap
# Description: SQLAlchemy database model defining regional inflation state metrics.

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base


class HeatmapData(Base):
    __tablename__ = "heatmap_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_name = Column(String, unique=True, nullable=False, index=True)
    region = Column(String, nullable=False, index=True)
    current_rate = Column(Float, nullable=False)
    year_ago_rate = Column(Float, nullable=False)
    threat_level = Column(String, nullable=False)  # 'Low', 'Medium', 'High'
    updated_at = Column(DateTime, default=datetime.utcnow)
