# Package: app.models
# Description: Unified DB models package exposing schemas to Alembic config env.py.

from app.core.database import Base
from app.models.user import User
from app.models.forecast import Forecast
from app.models.cpi import InflationData, CPIData
from app.models.news import NewsItem
from app.models.currency import CurrencyData
from app.models.alert import AlertRule, AlertLog, UserNotificationPreference, AlertNotification, AlertEvaluationLog
from app.models.simulation import Simulation
from app.models.heatmap import HeatmapData
from app.models.log import AuditLog, CopilotConversation, CopilotMessage
from app.models.explainability import ForecastExplainability
from app.models.rag import RagDocument, RagChunk, RagRetrievalLog

# Expose Base metadata for migration auto-generation
metadata = Base.metadata
