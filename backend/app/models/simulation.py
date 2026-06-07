# Module: app.models.simulation
# Description: SQLAlchemy database model defining scenario simulation runs variables.

from datetime import datetime
from sqlalchemy import Column, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    input_crude_change = Column(Float, nullable=False)
    input_rate_change = Column(Float, nullable=False)
    input_currency_change = Column(Float, nullable=False)
    output_projected_rate = Column(Float, nullable=False)
    executed_at = Column(DateTime, default=datetime.utcnow)

    # ORM Relationships
    user = relationship("User", back_populates="simulations")
