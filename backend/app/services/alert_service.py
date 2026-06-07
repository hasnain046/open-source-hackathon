# Module: app.services.alert_service
# Description: Core alert evaluation engine and service managing alert CRUD, preferences, notifications queue, and digests.

import uuid
import logging
import pytz
from datetime import datetime, timedelta, time
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import jinja2

from app.models.alert import AlertRule, AlertLog, UserNotificationPreference, AlertNotification, AlertEvaluationLog
from app.models.forecast import Forecast
from app.models.currency import CurrencyData
from app.models.news import NewsSignal
from app.models.rag import RagDocument
from app.models.cpi import InflationData
from app.schemas.alert import AlertRuleCreateSchema, AlertRuleUpdateSchema

from app.services.email_service import EmailService
from app.services.telegram_service import TelegramBotService
from app.services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)


class AlertService:
    @staticmethod
    def get_mock_logs():
        """Get realistic mock alert logs matching frontend specifications."""
        base_time = datetime(2026, 6, 6)
        return [
            {
                "id": uuid.UUID("a1111111-1111-1111-1111-111111111111"),
                "alert_id": uuid.UUID("f1111111-1111-1111-1111-111111111111"),
                "title": "CPI Headline Update",
                "message": "India CPI for May 2026 drops to 4.82%, lower than Wall Street estimates of 4.90%.",
                "severity": "Low",
                "triggered_at": base_time,
                "read": False,
                "channel": "System"
            },
            {
                "id": uuid.UUID("b2222222-2222-2222-2222-222222222222"),
                "alert_id": uuid.UUID("f2222222-2222-2222-2222-222222222222"),
                "title": "Vegetable Spike Warning",
                "message": "Agriculture price sub-indices indicate a 12% rise in wholesale potato & onion prices over 7 days.",
                "severity": "High",
                "triggered_at": base_time - timedelta(days=2),
                "read": False,
                "channel": "Email & Telegram"
            },
            {
                "id": uuid.UUID("c3333333-3333-3333-3333-333333333333"),
                "alert_id": uuid.UUID("f3333333-3333-3333-3333-333333333333"),
                "title": "Oil Threshold Triggered",
                "message": "Brent Crude falls below your preset trigger of $80.00/bbl (currently trading at $77.80).",
                "severity": "Medium",
                "triggered_at": base_time - timedelta(days=4),
                "read": True,
                "channel": "System"
            },
            {
                "id": uuid.UUID("d4444444-4444-4444-4444-444444444444"),
                "alert_id": uuid.UUID("f4444444-4444-4444-4444-444444444444"),
                "title": "Exchange Rate Alert",
                "message": "USD/INR dips below 82.60, strengthening the Rupee and lowering commodity landing costs.",
                "severity": "Medium",
                "triggered_at": base_time - timedelta(days=9),
                "read": True,
                "channel": "Telegram"
            }
        ]

    @staticmethod
    def get_user_logs(user_id: str, db: Session):
        """Retrieve triggered alarms lists for user by joining logs and rules."""
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            db_logs = db.query(AlertLog).join(AlertRule).filter(AlertRule.user_id == user_uuid).all()
            if db_logs:
                return db_logs
        except Exception as e:
            logger.error(f"Database query failed in AlertService.get_user_logs: {e}")
        return AlertService.get_mock_logs()

    @staticmethod
    def get_user_rules(user_id: uuid.UUID, db: Session) -> List[AlertRule]:
        return db.query(AlertRule).filter(AlertRule.user_id == user_id).all()

    @staticmethod
    def get_rule(user_id: uuid.UUID, rule_id: uuid.UUID, db: Session) -> Optional[AlertRule]:
        return db.query(AlertRule).filter(AlertRule.id == rule_id, AlertRule.user_id == user_id).first()

    @staticmethod
    def add_rule(user_id: uuid.UUID, rule: AlertRuleCreateSchema, db: Session) -> AlertRule:
        """Register custom threshold rule targets."""
        db_rule = AlertRule(
            id=uuid.uuid4(),
            user_id=user_id,
            rule_name=rule.rule_name,
            alert_type=rule.alert_type,
            indicator=rule.indicator,
            condition_operator=rule.condition_operator,
            threshold_value=rule.threshold_value,
            horizon_days=rule.horizon_days,
            cooldown_hours=rule.cooldown_hours,
            delta_threshold=rule.delta_threshold,
            email_channel=rule.email_channel,
            telegram_channel=rule.telegram_channel,
            whatsapp_channel=rule.whatsapp_channel,
            rag_keywords=rule.rag_keywords,
            is_active=rule.is_active,
            created_at=datetime.utcnow()
        )
        try:
            db.add(db_rule)
            db.commit()
            db.refresh(db_rule)
        except Exception as e:
            db.rollback()
            logger.error(f"Database save failed in AlertService.add_rule: {e}")
            raise e
        return db_rule

    @staticmethod
    def update_rule(user_id: uuid.UUID, rule_id: uuid.UUID, schema: AlertRuleUpdateSchema, db: Session) -> Optional[AlertRule]:
        db_rule = db.query(AlertRule).filter(AlertRule.id == rule_id, AlertRule.user_id == user_id).first()
        if not db_rule:
            return None
        
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_rule, key, value)
            
        try:
            db.add(db_rule)
            db.commit()
            db.refresh(db_rule)
        except Exception as e:
            db.rollback()
            logger.error(f"Database update failed in AlertService.update_rule: {e}")
            raise e
        return db_rule

    @staticmethod
    def remove_rule(user_id: str, rule_id: str, db: Session) -> bool:
        """Remove active alarm rules."""
        try:
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            rule_uuid = uuid.UUID(rule_id) if isinstance(rule_id, str) else rule_id
            db_rule = db.query(AlertRule).filter(
                AlertRule.id == rule_uuid,
                AlertRule.user_id == user_uuid
            ).first()
            
            if db_rule:
                db.delete(db_rule)
                db.commit()
                return True
        except Exception as e:
            db.rollback()
            logger.error(f"Database delete failed in AlertService.remove_rule: {e}")
        return False

    @staticmethod
    def get_preferences(user_id: uuid.UUID, db: Session) -> UserNotificationPreference:
        pref = db.query(UserNotificationPreference).filter(UserNotificationPreference.user_id == user_id).first()
        if not pref:
            # Create default preferences
            pref = UserNotificationPreference(
                id=uuid.uuid4(),
                user_id=user_id,
                email_enabled=True,
                telegram_enabled=False,
                whatsapp_enabled=False,
                email_digest_mode="instant",
                min_severity="low",
                copilot_mode="analyst",
                daily_alert_limit=20,
                created_at=datetime.utcnow()
            )
            try:
                db.add(pref)
                db.commit()
                db.refresh(pref)
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to create default preferences: {e}")
        return pref

    @staticmethod
    def update_preferences(user_id: uuid.UUID, schema: Any, db: Session) -> UserNotificationPreference:
        pref = AlertService.get_preferences(user_id, db)
        update_data = schema.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(pref, key, value)
        try:
            db.add(pref)
            db.commit()
            db.refresh(pref)
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update preferences: {e}")
            raise e
        return pref


class AlertEvaluationEngine:
    @staticmethod
    def evaluate_operator(val: float, op: str, threshold: float) -> bool:
        if op == ">": return val > threshold
        if op == "<": return val < threshold
        if op == ">=": return val >= threshold
        if op == "<=": return val <= threshold
        if op == "==": return val == threshold
        if op == "!=": return val != threshold
        return False

    @staticmethod
    def determine_severity(val: float, alert_type: str, delta: Optional[float] = None) -> str:
        # Rule severity rules
        # Critical: Score >= 8.0 or forecast shift >= 1.0%
        # High: Score 6.0-7.9 or forecast shift 0.5-0.99%
        # Medium: Score 4.0-5.9 or forecast shift 0.3-0.49%
        # Low: Score < 4.0 or shift < 0.3%
        score = val
        if alert_type == "forecast_change" and delta is not None:
            score = delta * 10.0  # Scale up percentage delta for mapping, e.g. 1.0% -> 10.0 score, 0.5% -> 5.0 score

        if score >= 8.0:
            return "critical"
        elif score >= 6.0:
            return "high"
        elif score >= 4.0:
            return "medium"
        else:
            return "low"

    @classmethod
    def run(cls, db: Session) -> Dict[str, Any]:
        """Evaluates all active alert rules and enqueues notifications."""
        start_time = datetime.utcnow()
        rules = db.query(AlertRule).filter(AlertRule.is_active == True).all()
        rules_evaluated = 0
        rules_fired = 0
        notifications_enqueued = 0
        errors = {}

        # Pre-cache latest metrics for efficient lookup
        latest_currency = db.query(CurrencyData).order_by(CurrencyData.recording_date.desc()).first()
        latest_news = db.query(NewsSignal).order_by(NewsSignal.recording_date.desc()).first()
        forecasts = db.query(Forecast).order_by(Forecast.generated_at.desc()).all()
        latest_inflation = db.query(InflationData).order_by(InflationData.reporting_date.desc()).first()

        for rule in rules:
            try:
                rules_evaluated += 1
                now = datetime.utcnow()

                # 1. Cooldown Check
                if rule.last_triggered_at and rule.cooldown_hours:
                    cooldown_delta = timedelta(hours=rule.cooldown_hours)
                    if rule.last_triggered_at + cooldown_delta > now:
                        logger.debug(f"Rule {rule.id} is in cooldown.")
                        continue

                # 2. User Preferences and Limits/Quiet Hours Check
                pref = db.query(UserNotificationPreference).filter(UserNotificationPreference.user_id == rule.user_id).first()
                if not pref:
                    # Fallback default preferences
                    pref = UserNotificationPreference(email_enabled=True, email_digest_mode="instant", min_severity="low", daily_alert_limit=20)
                
                # Quiet Hours Check
                if pref.quiet_hours_start and pref.quiet_hours_end:
                    try:
                        tz = pytz.timezone(pref.quiet_hours_timezone or "Asia/Kolkata")
                        now_tz = datetime.now(tz)
                        start_t = datetime.strptime(pref.quiet_hours_start, "%H:%M").time()
                        end_t = datetime.strptime(pref.quiet_hours_end, "%H:%M").time()
                        curr_t = now_tz.time()

                        in_quiet = False
                        if start_t <= end_t:
                            in_quiet = (start_t <= curr_t <= end_t)
                        else:
                            in_quiet = (curr_t >= start_t or curr_t <= end_t)

                        if in_quiet:
                            logger.info(f"Suppressed alert evaluation for user {rule.user_id} due to quiet hours.")
                            continue
                    except Exception as q_err:
                        logger.warning(f"Error checking quiet hours for user {rule.user_id}: {q_err}")

                # Daily limit check
                daily_limit = pref.daily_alert_limit or 20
                twenty_four_hours_ago = now - timedelta(days=1)
                notifications_sent_today = db.query(AlertNotification).filter(
                    AlertNotification.user_id == rule.user_id,
                    AlertNotification.created_at >= twenty_four_hours_ago
                ).count()

                if notifications_sent_today >= daily_limit:
                    logger.info(f"User {rule.user_id} exceeded daily alert limit.")
                    continue

                # 3. Retrieve metric value based on alert type
                triggered = False
                trigger_value = None
                threshold_value = rule.threshold_value
                subject = ""
                body = ""

                if rule.alert_type == "threshold":
                    # Latest Forecast for horizon
                    latest_f = None
                    if rule.horizon_days:
                        for f in forecasts:
                            if abs((f.target_date - f.generated_at).days - rule.horizon_days) <= 5:
                                latest_f = f
                                break
                    else:
                        latest_f = forecasts[0] if forecasts else None

                    if latest_f:
                        trigger_value = latest_f.projected_rate
                        triggered = cls.evaluate_operator(trigger_value, rule.condition_operator, threshold_value)
                        if triggered:
                            subject = f"Inflation Forecast Exceeded {threshold_value}%"
                            body = f"The {rule.horizon_days or 30}-day inflation forecast has crossed your configured threshold. Projected rate: {trigger_value}% (threshold: {threshold_value}%)."

                elif rule.alert_type == "forecast_change":
                    matching_f = []
                    if rule.horizon_days:
                        for f in forecasts:
                            if abs((f.target_date - f.generated_at).days - rule.horizon_days) <= 5:
                                matching_f.append(f)
                                if len(matching_f) == 2:
                                    break
                    else:
                        matching_f = forecasts[:2]

                    if len(matching_f) >= 2:
                        trigger_value = matching_f[0].projected_rate
                        delta = trigger_value - matching_f[1].projected_rate
                        delta_thresh = rule.delta_threshold or threshold_value or 0.3
                        triggered = abs(delta) >= delta_thresh
                        if triggered:
                            subject = f"Forecast Shift Detected"
                            body = f"The projected rate has shifted by {delta:.2f}% (threshold: {delta_thresh}%). Current rate: {trigger_value}%, previous: {matching_f[1].projected_rate}%."

                elif rule.alert_type == "currency_shock":
                    if latest_currency and rule.indicator:
                        trigger_value = getattr(latest_currency, rule.indicator, None)
                        if trigger_value is not None:
                            triggered = cls.evaluate_operator(trigger_value, rule.condition_operator, threshold_value)
                            if triggered:
                                subject = f"Currency/Commodity Shock Detected"
                                body = f"Shock score for {rule.indicator} is {trigger_value} (threshold: {threshold_value})."

                elif rule.alert_type == "news_risk":
                    if latest_news and rule.indicator:
                        trigger_value = getattr(latest_news, rule.indicator, None)
                        if trigger_value is not None:
                            triggered = cls.evaluate_operator(trigger_value, rule.condition_operator, threshold_value)
                            if triggered:
                                subject = f"News Intelligence Risk Alert"
                                body = f"Risk score for {rule.indicator} is {trigger_value} (threshold: {threshold_value})."

                elif rule.alert_type == "model_drift":
                    # Compute forecast vs actual
                    if latest_inflation:
                        # Find forecast targeting this reporting date
                        fc = db.query(Forecast).filter(Forecast.target_date == latest_inflation.reporting_date).order_by(Forecast.generated_at.desc()).first()
                        if fc:
                            trigger_value = abs(fc.projected_rate - latest_inflation.headline_rate)
                            triggered = trigger_value >= threshold_value
                            if triggered:
                                subject = f"Model Drift Detected"
                                body = f"Model drift has exceeded the drift threshold. Projected: {fc.projected_rate}%, Actual: {latest_inflation.headline_rate}% (drift: {trigger_value:.2f}%)."
                        else:
                            # Or model_retrain_overdue check
                            latest_f = forecasts[0] if forecasts else None
                            if latest_f:
                                days_since_last = (now - latest_f.generated_at).days
                                triggered = days_since_last >= threshold_value
                                if triggered:
                                    trigger_value = float(days_since_last)
                                    subject = f"Model Retraining Overdue"
                                    body = f"Forecast model retrain overdue. Days since last forecast generation: {days_since_last} days (threshold: {threshold_value} days)."

                elif rule.alert_type == "rag_intelligence":
                    # Retrieve newly indexed RAG Documents
                    time_thresh = rule.last_triggered_at or (now - timedelta(minutes=60))
                    new_docs = db.query(RagDocument).filter(
                        RagDocument.ingestion_status == "indexed",
                        RagDocument.created_at > time_thresh
                    ).all()

                    keywords = rule.rag_keywords or pref.rag_alert_keywords or []
                    for doc in new_docs:
                        # Match title or chunks keywords
                        match = False
                        matched_kw = []
                        for kw in keywords:
                            if kw.lower() in doc.title.lower():
                                match = True
                                matched_kw.append(kw)
                        
                        if match:
                            triggered = True
                            trigger_value = 1.0
                            subject = f"RAG Document Keyword Match"
                            body = f"New document indexed: '{doc.title}' matches registered keywords: {', '.join(matched_kw)}."
                            break

                # 4. Trigger alert if condition is met
                if triggered:
                    rules_fired += 1
                    severity = cls.determine_severity(trigger_value or 0.0, rule.alert_type, trigger_value)
                    
                    # Log rule updates
                    rule.last_triggered_at = now
                    rule.trigger_count += 1
                    db.add(rule)

                    # Determine channels to enqueue
                    channels = []
                    if rule.email_channel and pref.email_enabled:
                        channels.append("email")
                    if rule.telegram_channel and pref.telegram_enabled and pref.telegram_chat_id:
                        channels.append("telegram")
                    if rule.whatsapp_channel and pref.whatsapp_enabled and pref.whatsapp_phone:
                        channels.append("whatsapp")

                    # If no channels are enabled, log anyway for audit trail
                    if not channels:
                        channels.append("log_only")

                    for ch in channels:
                        status = "pending"
                        if ch == "email" and pref.email_digest_mode in ["daily", "weekly"]:
                            status = "pending_digest"
                        elif ch == "log_only":
                            status = "logged_only"

                        # Create notification
                        notification = AlertNotification(
                            id=uuid.uuid4(),
                            alert_rule_id=rule.id,
                            user_id=rule.user_id,
                            alert_type=rule.alert_type or "system",
                            severity=severity,
                            channel=ch if ch != "log_only" else "email",
                            subject=subject,
                            body=body,
                            trigger_value=trigger_value,
                            threshold_value=threshold_value,
                            status=status,
                            created_at=now
                        )
                        db.add(notification)
                        notifications_enqueued += 1

                        # Create AlertLog for backward compatibility
                        alert_log = AlertLog(
                            id=uuid.uuid4(),
                            alert_id=rule.id,
                            title=subject,
                            message=body,
                            severity=severity.capitalize(),
                            channel=ch.capitalize(),
                            read=False,
                            triggered_at=now,
                            alert_type=rule.alert_type,
                            trigger_value=trigger_value,
                            delivered=(status == "sent"),
                            notification_id=notification.id
                        )
                        db.add(alert_log)

                db.commit()

            except Exception as rule_err:
                db.rollback()
                logger.error(f"Error evaluating rule {rule.id}: {rule_err}")
                errors[str(rule.id)] = str(rule_err)

        # 5. Record evaluation logs metrics
        latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        eval_log = AlertEvaluationLog(
            id=uuid.uuid4(),
            evaluated_at=start_time,
            rules_evaluated=rules_evaluated,
            rules_fired=rules_fired,
            notifications_enqueued=notifications_enqueued,
            evaluation_latency_ms=latency,
            errors=errors if errors else None
        )
        try:
            db.add(eval_log)
            db.commit()
        except Exception as log_err:
            db.rollback()
            logger.error(f"Failed to save evaluation log: {log_err}")

        # Send pending notifications right away in this cycle
        cls.send_pending_notifications(db)

        return {
            "rules_evaluated": rules_evaluated,
            "rules_fired": rules_fired,
            "notifications_enqueued": notifications_enqueued,
            "latency_ms": latency
        }

    @classmethod
    def send_pending_notifications(cls, db: Session):
        """Processes the notifications queue, handles retries with backoff."""
        now = datetime.utcnow()
        pending = db.query(AlertNotification).filter(
            AlertNotification.status.in_(["pending", "retrying"]),
            (AlertNotification.next_retry_at == None) | (AlertNotification.next_retry_at <= now)
        ).all()

        for notif in pending:
            try:
                success = False
                error_msg = None

                # Fetch recipient preferences for copilot mode formatting
                pref = db.query(UserNotificationPreference).filter(UserNotificationPreference.user_id == notif.user_id).first()
                copilot_mode = pref.copilot_mode if pref else "analyst"

                # Render template body depending on mode
                rendered_subject = notif.subject
                rendered_body = notif.body
                if copilot_mode == "executive":
                    rendered_subject = f"⚠️ BRIEF: {notif.subject}"
                    rendered_body = f"Summary: {notif.body}\nAction recommended: Review economic impact parameters."
                elif copilot_mode == "economist":
                    rendered_subject = f"📊 ANALYSIS: {notif.subject}"
                    rendered_body = f"Economic Signal: {notif.body}\nAnalysis context: Forecast Model Delta check evaluated."

                # Send via channel
                if notif.channel == "email":
                    html_content = f"<html><body><h3>{rendered_subject}</h3><p>{rendered_body}</p><hr/><p>Manage alerts: <a href='https://inflationiq.ai/alerts/preferences'>Preferences</a></p></body></html>"
                    success = EmailService.send(
                        to_email=notif.user.email,
                        subject=rendered_subject,
                        html_body=html_content,
                        text_body=rendered_body
                    )
                elif notif.channel == "telegram" and pref and pref.telegram_chat_id:
                    tg_msg = f"*{rendered_subject}*\n\n{rendered_body}"
                    success = TelegramBotService.send(
                        chat_id=pref.telegram_chat_id,
                        message_text=tg_msg
                    )
                elif notif.channel == "whatsapp" and pref and pref.whatsapp_phone:
                    # Map parameters based on alert type for templates
                    variables = [
                        notif.alert_type,
                        str(notif.trigger_value or 0.0),
                        str(notif.threshold_value or 0.0)
                    ]
                    success = WhatsAppService.send(
                        phone_number=pref.whatsapp_phone,
                        template_name=f"{notif.alert_type}_alert",
                        template_variables=variables
                    )
                else:
                    # Mock/console fallback or logged_only status
                    success = True

                if success:
                    notif.status = "sent" if notif.channel != "log_only" else "logged_only"
                    notif.delivered_at = datetime.utcnow()
                    
                    # Update backward compatible AlertLog
                    alert_log = db.query(AlertLog).filter(AlertLog.notification_id == notif.id).first()
                    if alert_log:
                        alert_log.delivered = True
                        db.add(alert_log)
                else:
                    raise RuntimeError("Channel sending returned false status.")

            except Exception as e:
                error_msg = str(e)
                notif.retry_count += 1
                if notif.retry_count >= 5:
                    notif.status = "failed"
                    notif.error_message = error_msg
                else:
                    notif.status = "retrying"
                    # Backoff formula: delay = 5 * 2^(retry_count - 1) minutes
                    delay_min = 5 * (2 ** (notif.retry_count - 1))
                    notif.next_retry_at = datetime.utcnow() + timedelta(minutes=delay_min)
                    notif.error_message = error_msg

            db.add(notif)
            db.commit()

    @classmethod
    def send_digests(cls, db: Session, digest_mode: str):
        """Aggregates all pending_digest emails for users and sends a unified message."""
        # Query all notifications in pending_digest status for the channel 'email'
        pending = db.query(AlertNotification).filter(
            AlertNotification.status == "pending_digest",
            AlertNotification.channel == "email"
        ).all()

        # Group by user_id
        user_notifications = {}
        for notif in pending:
            user_notifications.setdefault(notif.user_id, []).append(notif)

        for user_id, notifs in user_notifications.items():
            try:
                # Get User entity
                user = notifs[0].user
                pref = db.query(UserNotificationPreference).filter(UserNotificationPreference.user_id == user_id).first()
                # Check user preferences matching digest mode to avoid sending if preference updated
                if pref and pref.email_digest_mode != digest_mode:
                    continue

                subject = f"InflationIQ {digest_mode.capitalize()} Alerts Digest — {len(notifs)} Notifications"
                
                # Format digest HTML body
                digest_lines = []
                for n in notifs:
                    digest_lines.append(f"<li><strong>[{n.severity.upper()}] {n.subject}</strong>: {n.body} (Fired at: {n.created_at.strftime('%Y-%m-%d %H:%M:%S')})</li>")
                
                html_body = f"""
                <html>
                <body>
                    <h2>Your {digest_mode.capitalize()} InflationIQ Alerts Digest</h2>
                    <p>Here is a summary of the alerts triggered over the last period:</p>
                    <ul>
                        {"".join(digest_lines)}
                    </ul>
                    <hr/>
                    <p>Manage notification preferences: <a href='https://inflationiq.ai/alerts/preferences'>Preferences</a></p>
                </body>
                </html>
                """
                text_body = f"Your {digest_mode.capitalize()} InflationIQ Alerts Digest:\n\n" + "\n".join([f"- [{n.severity.upper()}] {n.subject}: {n.body}" for n in notifs])

                # Send unified email
                success = EmailService.send(
                    to_email=user.email,
                    subject=subject,
                    html_body=html_body,
                    text_body=text_body
                )

                if success:
                    # Update status for all compiled notifications
                    for n in notifs:
                        n.status = "sent"
                        n.delivered_at = datetime.utcnow()
                        db.add(n)
                        
                        alert_log = db.query(AlertLog).filter(AlertLog.notification_id == n.id).first()
                        if alert_log:
                            alert_log.delivered = True
                            db.add(alert_log)
                    db.commit()

            except Exception as e:
                db.rollback()
                logger.error(f"Failed to send digest for user {user_id}: {e}")
