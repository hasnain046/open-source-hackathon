# Module: app.api.v1.alerts
# Description: Router handling user alert rules creation, CRUD, notification history, preferences, and multi-channel integrations.

from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.api.deps import get_db, get_current_user
from app.schemas.alert import (
    AlertRuleCreateSchema, AlertRuleUpdateSchema, AlertRuleResponseSchema,
    AlertLogResponseSchema, UserNotificationPreferenceSchema,
    UserNotificationPreferenceResponseSchema, AlertNotificationResponseSchema,
    AlertEvaluationLogResponseSchema
)
from app.services.alert_service import AlertService, AlertEvaluationEngine
from app.services.telegram_service import TelegramBotService
from app.services.whatsapp_service import WhatsAppService
from app.models.user import User
from app.models.alert import AlertRule, AlertNotification, AlertEvaluationLog, UserNotificationPreference
from app.config import settings

router = APIRouter(prefix="/alerts", tags=["Alerts & Triggers"])


# ==========================================
# Alert Rules CRUD
# ==========================================

@router.get("/rules", response_model=List[AlertRuleResponseSchema])
def list_alert_rules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all alert rules for the authenticated user."""
    return AlertService.get_user_rules(current_user.id, db)


@router.post("/rules", response_model=AlertRuleResponseSchema, status_code=status.HTTP_201_CREATED)
def create_alert_rule(
    rule: AlertRuleCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register a new conditional indicator trigger condition."""
    return AlertService.add_rule(current_user.id, rule, db)


@router.get("/rules/{id}", response_model=AlertRuleResponseSchema)
def get_alert_rule(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detail of a single alert rule."""
    rule = AlertService.get_rule(current_user.id, id, db)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found."
        )
    return rule


@router.put("/rules/{id}", response_model=AlertRuleResponseSchema)
def update_alert_rule(
    id: UUID,
    schema: AlertRuleUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing alert rule."""
    rule = AlertService.update_rule(current_user.id, id, schema, db)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found."
        )
    return rule


@router.delete("/rules/{id}", status_code=status.HTTP_200_OK)
def delete_alert_rule(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deregister an active indicator trigger rule."""
    success = AlertService.remove_rule(current_user.id, id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found or permission denied."
        )
    return {"message": f"Alert rule {id} successfully removed"}


@router.post("/rules/{id}/test", status_code=status.HTTP_200_OK)
def test_alert_rule(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger evaluation for a specific alert rule."""
    rule = db.query(AlertRule).filter(AlertRule.id == id, AlertRule.user_id == current_user.id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert rule not found."
        )
    
    # Temporarily ignore cooldown for testing
    orig_triggered = rule.last_triggered_at
    rule.last_triggered_at = None
    db.add(rule)
    db.commit()

    # Re-evaluate
    res = AlertEvaluationEngine.run(db)
    return {
        "message": "Manual rule evaluation completed.",
        "details": res
    }


# ==========================================
# User Preferences
# ==========================================

@router.get("/preferences", response_model=UserNotificationPreferenceResponseSchema)
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve notification preferences for the current user."""
    return AlertService.get_preferences(current_user.id, db)


@router.put("/preferences", response_model=UserNotificationPreferenceResponseSchema)
def update_preferences(
    schema: UserNotificationPreferenceSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update notification preferences for the current user."""
    return AlertService.update_preferences(current_user.id, schema, db)


# ==========================================
# Telegram Integration Connect / Webhook / Webhook Mock
# ==========================================

@router.get("/telegram/connect", status_code=status.HTTP_200_OK)
def telegram_connect(
    current_user: User = Depends(get_current_user)
):
    """Get a one-time connection token for Telegram linking."""
    token = TelegramBotService.generate_connection_token(current_user.id)
    return {
        "token": token,
        "bot_link": f"https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={token}"
    }


@router.get("/telegram/status", status_code=status.HTTP_200_OK)
def telegram_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check Telegram connection status."""
    pref = AlertService.get_preferences(current_user.id, db)
    return {
        "connected": pref.telegram_chat_id is not None,
        "chat_id": pref.telegram_chat_id
    }


@router.post("/telegram/simulate-bot-start", status_code=status.HTTP_200_OK)
def simulate_telegram_bot_start(
    token: str,
    chat_id: str,
    db: Session = Depends(get_db)
):
    """Mock/simulate Telegram bot receiving start command with token."""
    user_id = TelegramBotService.verify_token(token, chat_id)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired connection token."
        )
    pref = AlertService.get_preferences(user_id, db)
    pref.telegram_chat_id = chat_id
    pref.telegram_enabled = True
    db.add(pref)
    db.commit()
    return {"message": "Telegram connection verified successfully and saved."}


# ==========================================
# WhatsApp Integration Connect / Verify
# ==========================================

@router.post("/whatsapp/connect", status_code=status.HTTP_200_OK)
def whatsapp_connect(
    phone_number: str,
    current_user: User = Depends(get_current_user)
):
    """Register phone number and send OTP for WhatsApp alerts verification."""
    otp = WhatsAppService.generate_and_send_otp(phone_number)
    return {
        "message": "OTP verification code sent via WhatsApp.",
        "otp_mock": otp  # Exposed for testing/convenience
    }


@router.post("/whatsapp/verify", status_code=status.HTTP_200_OK)
def whatsapp_verify(
    phone_number: str,
    otp: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify WhatsApp OTP and enable the channel."""
    success = WhatsAppService.verify_otp(phone_number, otp)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect OTP code or expired session."
        )
    pref = AlertService.get_preferences(current_user.id, db)
    pref.whatsapp_phone = phone_number
    pref.whatsapp_enabled = True
    db.add(pref)
    db.commit()
    return {"message": "WhatsApp number verified and enabled successfully."}


@router.get("/whatsapp/status", status_code=status.HTTP_200_OK)
def whatsapp_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check WhatsApp connection status."""
    pref = AlertService.get_preferences(current_user.id, db)
    return {
        "connected": pref.whatsapp_phone is not None,
        "phone": pref.whatsapp_phone
    }


# ==========================================
# History Logs
# ==========================================

@router.get("/logs", response_model=List[AlertLogResponseSchema])
def get_alert_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve list of triggered alert messages (backward compatibility)."""
    return AlertService.get_user_logs(current_user.id, db)


@router.get("/notifications", response_model=List[AlertNotificationResponseSchema])
def get_notifications(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get paginated history of all sent or failed alert notifications."""
    return db.query(AlertNotification).filter(
        AlertNotification.user_id == current_user.id
    ).order_by(AlertNotification.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/evaluation-logs", response_model=List[AlertEvaluationLogResponseSchema])
def get_evaluation_logs(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve evaluation engine cycle run logs (Admin only)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permission required to view evaluation logs."
        )
    return db.query(AlertEvaluationLog).order_by(AlertEvaluationLog.evaluated_at.desc()).offset(skip).limit(limit).all()
