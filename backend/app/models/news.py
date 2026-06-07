# Module: app.models.news
# Description: SQLAlchemy database model defining parsed financial news headlines.

from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from app.core.database import Base


class NewsItem(Base):
    __tablename__ = "news_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    headline = Column(String, nullable=False)
    source = Column(String, nullable=False)
    url = Column(String, nullable=True)
    category = Column(String, nullable=False, index=True)
    sentiment = Column(String, nullable=False, index=True)
    impact_score = Column(Float, nullable=False)
    published_at = Column(DateTime, nullable=False)

    # NLP & Signal Fields (Phase 8 additions)
    syndication_count = Column(Integer, default=1)
    sentiment_polarity = Column(Float, nullable=True)
    sentiment_neutral_prob = Column(Float, nullable=True)
    economic_risk_score = Column(Float, nullable=True)
    inflation_pressure_score = Column(Float, nullable=True)
    topic_label = Column(String, nullable=True, index=True)
    entities_json = Column(JSONB, nullable=True)
    regional_impact = Column(JSONB, nullable=True)


class NewsSignal(Base):
    __tablename__ = "news_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recording_date = Column(DateTime, unique=True, nullable=False, index=True)
    avg_sentiment = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    inflation_pressure = Column(Float, nullable=False)
    topic_volumes = Column(JSONB, nullable=True)
    google_trends_indices = Column(JSONB, nullable=True)
