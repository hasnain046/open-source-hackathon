# Module: app.models.alert
# Description: SQLAlchemy database models defining alert trigger rules, preferences, notifications, and logs.

from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base


class AlertRule(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    rule_name = Column(String, nullable=False)
    indicator = Column(String, nullable=True, index=True)
    condition_operator = Column(String, nullable=False)  # '>', '<', etc.
    threshold_value = Column(Float, nullable=False)
    email_channel = Column(Boolean, default=False)
    telegram_channel = Column(Boolean, default=False)
    whatsapp_channel = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Extended Phase 13 fields
    alert_type = Column(String, nullable=True)  # 'threshold', 'forecast_change', 'currency_shock', 'news_risk', 'model_drift', 'rag_intelligence'
    horizon_days = Column(Integer, nullable=True)
    cooldown_hours = Column(Float, default=6.0)
    delta_threshold = Column(Float, nullable=True)
    rag_keywords = Column(JSON, nullable=True)  # List of keywords
    last_triggered_at = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # ORM Relationships
    user = relationship("User", back_populates="alerts")


class UserNotificationPreference(Base):
    __tablename__ = "user_notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    email_enabled = Column(Boolean, default=True)
    telegram_enabled = Column(Boolean, default=False)
    whatsapp_enabled = Column(Boolean, default=False)
    telegram_chat_id = Column(String, nullable=True)
    whatsapp_phone = Column(String, nullable=True)
    email_digest_mode = Column(String, default="instant")  # 'instant', 'daily', 'weekly'
    quiet_hours_start = Column(String, nullable=True)  # 'HH:MM'
    quiet_hours_end = Column(String, nullable=True)    # 'HH:MM'
    quiet_hours_timezone = Column(String, default="Asia/Kolkata")
    min_severity = Column(String, default="low")      # 'low', 'medium', 'high', 'critical'
    copilot_mode = Column(String, default="analyst")  # 'analyst', 'economist', 'executive'
    rag_alert_keywords = Column(JSON, nullable=True)  # List of strings
    daily_alert_limit = Column(Integer, default=20)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ORM Relationship
    user = relationship("User", backref="notification_preference", uselist=False)


class AlertNotification(Base):
    __tablename__ = "alert_notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_rule_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    alert_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    channel = Column(String, nullable=False)  # 'email', 'telegram', 'whatsapp'
    subject = Column(String, nullable=True)
    body = Column(String, nullable=False)
    trigger_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    status = Column(String, default="pending")  # 'pending', 'sent', 'delivered', 'failed', 'retrying', 'logged_only', 'pending_digest'
    delivered_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    next_retry_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    alert_rule = relationship("AlertRule")
    user = relationship("User")


class AlertEvaluationLog(Base):
    __tablename__ = "alert_evaluation_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evaluated_at = Column(DateTime, default=datetime.utcnow)
    rules_evaluated = Column(Integer, nullable=False)
    rules_fired = Column(Integer, nullable=False)
    notifications_enqueued = Column(Integer, nullable=False)
    evaluation_latency_ms = Column(Integer, nullable=False)
    errors = Column(JSON, nullable=True)


class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=True, index=True)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    read = Column(Boolean, default=False)
    triggered_at = Column(DateTime, default=datetime.utcnow)

    # Extended Phase 13 fields
    alert_type = Column(String, nullable=True)
    trigger_value = Column(Float, nullable=True)
    delivered = Column(Boolean, default=False)
    notification_id = Column(UUID(as_uuid=True), ForeignKey("alert_notifications.id"), nullable=True)

    # ORM Relationships
    alert = relationship("AlertRule")
    notification = relationship("AlertNotification")

