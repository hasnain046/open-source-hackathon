# Module: app.schemas.alert
# Description: Pydantic schemas defining alarm trigger conditions rules, user preferences, notifications, and evaluation logs.

from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional


class AlertRuleBase(BaseModel):
    rule_name: str = Field(..., min_length=3)
    alert_type: str = Field(..., description="Alert category (e.g. threshold, forecast_change, currency_shock, news_risk, model_drift, rag_intelligence)")
    indicator: Optional[str] = Field(None, description="Macro parameter (e.g. Brent Crude, projected_rate)")
    condition_operator: str = Field(..., description="Logical comparator (e.g. > or <)")
    threshold_value: float = Field(..., description="Trigger threshold value index")
    horizon_days: Optional[int] = Field(None, description="Forecast horizon days (30/60/90/180/365)")
    cooldown_hours: float = Field(6.0, description="Cooldown in hours")
    delta_threshold: Optional[float] = Field(None, description="Minimum change magnitude for forecast_change")
    email_channel: bool = Field(False)
    telegram_channel: bool = Field(False)
    whatsapp_channel: bool = Field(False)
    rag_keywords: Optional[List[str]] = Field(None, description="Keywords for RAG Intelligence alerts")
    is_active: bool = Field(True)


class AlertRuleCreateSchema(AlertRuleBase):
    pass


class AlertRuleUpdateSchema(BaseModel):
    rule_name: Optional[str] = None
    alert_type: Optional[str] = None
    indicator: Optional[str] = None
    condition_operator: Optional[str] = None
    threshold_value: Optional[float] = None
    horizon_days: Optional[int] = None
    cooldown_hours: Optional[float] = None
    delta_threshold: Optional[float] = None
    email_channel: Optional[bool] = None
    telegram_channel: Optional[bool] = None
    whatsapp_channel: Optional[bool] = None
    rag_keywords: Optional[List[str]] = None
    is_active: Optional[bool] = None


class AlertRuleResponseSchema(AlertRuleBase):
    id: UUID
    user_id: UUID
    trigger_count: int
    last_triggered_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Backward compatibility
class AlertRuleSchema(BaseModel):
    rule_name: str = Field(..., min_length=3)
    indicator: str = Field(..., description="Macro parameter (e.g. Brent Crude)")
    condition_operator: str = Field(..., description="Logical comparator (e.g. > or <)")
    threshold_value: float = Field(..., description="Trigger threshold value index")
    email_channel: bool = Field(False)
    telegram_channel: bool = Field(False)

    class Config:
        from_attributes = True


class UserNotificationPreferenceSchema(BaseModel):
    email_enabled: bool = Field(True)
    telegram_enabled: bool = Field(False)
    whatsapp_enabled: bool = Field(False)
    telegram_chat_id: Optional[str] = Field(None)
    whatsapp_phone: Optional[str] = Field(None)
    email_digest_mode: str = Field("instant", description="instant, daily, weekly")
    quiet_hours_start: Optional[str] = Field(None, description="HH:MM format")
    quiet_hours_end: Optional[str] = Field(None, description="HH:MM format")
    quiet_hours_timezone: str = Field("Asia/Kolkata")
    min_severity: str = Field("low", description="low, medium, high, critical")
    copilot_mode: str = Field("analyst", description="analyst, economist, executive")
    rag_alert_keywords: Optional[List[str]] = Field(None)
    daily_alert_limit: int = Field(20)

    class Config:
        from_attributes = True


class UserNotificationPreferenceResponseSchema(UserNotificationPreferenceSchema):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class AlertNotificationResponseSchema(BaseModel):
    id: UUID
    alert_rule_id: Optional[UUID] = None
    user_id: UUID
    alert_type: str
    severity: str
    channel: str
    subject: Optional[str] = None
    body: str
    trigger_value: Optional[float] = None
    threshold_value: Optional[float] = None
    status: str
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int
    next_retry_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AlertEvaluationLogResponseSchema(BaseModel):
    id: UUID
    evaluated_at: datetime
    rules_evaluated: int
    rules_fired: int
    notifications_enqueued: int
    evaluation_latency_ms: int
    errors: Optional[dict] = None

    class Config:
        from_attributes = True


class AlertLogResponseSchema(BaseModel):
    id: UUID
    alert_id: Optional[UUID] = None
    title: str
    message: str
    severity: str
    channel: str
    read: bool
    triggered_at: datetime
    alert_type: Optional[str] = None
    trigger_value: Optional[float] = None
    delivered: bool = False
    notification_id: Optional[UUID] = None

    class Config:
        from_attributes = True
