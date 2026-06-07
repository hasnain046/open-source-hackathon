# Module: tests.test_alerts
# Description: Automated integration and unit tests for Phase 13: Alerts Automation.

import os
import sys
import unittest
import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.core.database import Base
from app.models.user import User
from app.models.alert import AlertRule, AlertLog, AlertNotification, UserNotificationPreference, AlertEvaluationLog
from app.models.forecast import Forecast
from app.models.currency import CurrencyData
from app.models.news import NewsSignal
from app.models.cpi import InflationData
from app.services.alert_service import AlertService, AlertEvaluationEngine
from app.api.deps import get_current_user, get_db

SQLITE_PATH = "sqlite:///" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "local_sqlite.db")).replace("\\", "/")

# Mock user for alerts
mock_user_id = uuid.uuid4()
mock_user = User(
    id=mock_user_id,
    email="alerts-tester@inflationiq.ai",
    full_name="Alerts Tester",
    role="analyst",
    is_active=True,
    created_at=datetime.utcnow()
)


class TestAlertsAutomation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine(SQLITE_PATH)
        Base.metadata.drop_all(bind=cls.engine)
        Base.metadata.create_all(bind=cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.db = self.Session()
        # Clean up database tables for alerts to ensure clean state
        self.db.query(AlertNotification).delete()
        self.db.query(AlertLog).delete()
        self.db.query(AlertRule).delete()
        self.db.query(AlertEvaluationLog).delete()
        self.db.query(UserNotificationPreference).delete()
        self.db.query(Forecast).delete()
        self.db.query(CurrencyData).delete()
        self.db.query(NewsSignal).delete()
        self.db.query(InflationData).delete()

        # Ensure user exists in local test DB
        self.db.query(User).filter(User.email == "alerts-tester@inflationiq.ai").delete()
        self.db.commit()

        self.db.add(User(
            id=mock_user_id,
            email="alerts-tester@inflationiq.ai",
            password_hash="mock_hash",
            full_name="Alerts Tester",
            role="analyst",
            is_active=True,
            created_at=datetime.utcnow()
        ))
        self.db.commit()

        self.client = TestClient(app)
        app.dependency_overrides[get_current_user] = lambda: mock_user
        app.dependency_overrides[get_db] = lambda: self.db

    def tearDown(self):
        self.db.close()
        app.dependency_overrides.clear()

    def test_preferences_api(self):
        """Test getting and updating user notification preferences."""
        headers = {"Authorization": "Bearer mock_token"}
        res = self.client.get("/api/v1/alerts/preferences", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["email_enabled"], True)
        self.assertEqual(data["email_digest_mode"], "instant")

        # Update preference
        payload = {
            "email_enabled": True,
            "telegram_enabled": True,
            "email_digest_mode": "daily",
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "quiet_hours_timezone": "Asia/Kolkata",
            "min_severity": "medium",
            "copilot_mode": "economist",
            "daily_alert_limit": 15
        }
        res_put = self.client.put("/api/v1/alerts/preferences", json=payload, headers=headers)
        self.assertEqual(res_put.status_code, 200)
        data_put = res_put.json()
        self.assertEqual(data_put["email_digest_mode"], "daily")
        self.assertEqual(data_put["quiet_hours_start"], "22:00")
        self.assertEqual(data_put["daily_alert_limit"], 15)

    def test_alert_rule_crud(self):
        """Test creating, reading, updating and deleting alert rules."""
        headers = {"Authorization": "Bearer mock_token"}
        # Create rule
        payload = {
            "rule_name": "Critical Oil Price Rule",
            "alert_type": "currency_shock",
            "indicator": "brent_crude_shock_score",
            "condition_operator": ">",
            "threshold_value": 7.5,
            "cooldown_hours": 3.0,
            "email_channel": True,
            "telegram_channel": False,
            "whatsapp_channel": False,
            "is_active": True
        }
        res_post = self.client.post("/api/v1/alerts/rules", json=payload, headers=headers)
        self.assertEqual(res_post.status_code, 201)
        rule_data = res_post.json()
        self.assertEqual(rule_data["rule_name"], "Critical Oil Price Rule")
        self.assertEqual(rule_data["threshold_value"], 7.5)
        rule_id = rule_data["id"]

        # List rules
        res_list = self.client.get("/api/v1/alerts/rules", headers=headers)
        self.assertEqual(res_list.status_code, 200)
        self.assertEqual(len(res_list.json()), 1)

        # Get rule detail
        res_get = self.client.get(f"/api/v1/alerts/rules/{rule_id}", headers=headers)
        self.assertEqual(res_get.status_code, 200)
        self.assertEqual(res_get.json()["rule_name"], "Critical Oil Price Rule")

        # Update rule
        update_payload = {"threshold_value": 8.0, "rule_name": "Oil Shock Alert"}
        res_put = self.client.put(f"/api/v1/alerts/rules/{rule_id}", json=update_payload, headers=headers)
        self.assertEqual(res_put.status_code, 200)
        self.assertEqual(res_put.json()["threshold_value"], 8.0)
        self.assertEqual(res_put.json()["rule_name"], "Oil Shock Alert")

        # Delete rule
        res_del = self.client.delete(f"/api/v1/alerts/rules/{rule_id}", headers=headers)
        self.assertEqual(res_del.status_code, 200)

        # Confirm deleted
        res_get_gone = self.client.get(f"/api/v1/alerts/rules/{rule_id}", headers=headers)
        self.assertEqual(res_get_gone.status_code, 404)

    def test_telegram_connection_endpoints(self):
        """Test Telegram connect token generation and simulate bot start linking."""
        headers = {"Authorization": "Bearer mock_token"}
        # Connect
        res_conn = self.client.get("/api/v1/alerts/telegram/connect", headers=headers)
        self.assertEqual(res_conn.status_code, 200)
        conn_data = res_conn.json()
        self.assertIn("token", conn_data)
        token = conn_data["token"]

        # Status before
        res_stat1 = self.client.get("/api/v1/alerts/telegram/status", headers=headers)
        self.assertEqual(res_stat1.status_code, 200)
        self.assertEqual(res_stat1.json()["connected"], False)

        # Simulate start command webhook/call
        res_sim = self.client.post(f"/api/v1/alerts/telegram/simulate-bot-start?token={token}&chat_id=987654321")
        self.assertEqual(res_sim.status_code, 200)

        # Status after
        res_stat2 = self.client.get("/api/v1/alerts/telegram/status", headers=headers)
        self.assertEqual(res_stat2.status_code, 200)
        self.assertEqual(res_stat2.json()["connected"], True)
        self.assertEqual(res_stat2.json()["chat_id"], "987654321")

    def test_whatsapp_connection_endpoints(self):
        """Test WhatsApp OTP send, verify, and enabling."""
        headers = {"Authorization": "Bearer mock_token"}
        # Connect phone
        res_conn = self.client.post("/api/v1/alerts/whatsapp/connect?phone_number=%2B919876543210", headers=headers)
        self.assertEqual(res_conn.status_code, 200)
        conn_data = res_conn.json()
        self.assertIn("otp_mock", conn_data)
        otp = conn_data["otp_mock"]

        # Status before
        res_stat1 = self.client.get("/api/v1/alerts/whatsapp/status", headers=headers)
        self.assertEqual(res_stat1.status_code, 200)
        self.assertEqual(res_stat1.json()["connected"], False)

        # Verify incorrect OTP
        res_verify_bad = self.client.post("/api/v1/alerts/whatsapp/verify?phone_number=%2B919876543210&otp=000000", headers=headers)
        self.assertEqual(res_verify_bad.status_code, 400)

        # Verify correct OTP
        res_verify_good = self.client.post(f"/api/v1/alerts/whatsapp/verify?phone_number=%2B919876543210&otp={otp}", headers=headers)
        self.assertEqual(res_verify_good.status_code, 200)

        # Status after
        res_stat2 = self.client.get("/api/v1/alerts/whatsapp/status", headers=headers)
        self.assertEqual(res_stat2.status_code, 200)
        self.assertEqual(res_stat2.json()["connected"], True)
        self.assertEqual(res_stat2.json()["phone"], "+919876543210")

    def test_rule_evaluation_threshold_breach(self):
        """Verify threshold breach rule evaluation triggers notification."""
        # Setup target forecast that breaches critical 6.0% threshold (e.g. projected 6.5%)
        now = datetime.utcnow()
        forecast = Forecast(
            id=uuid.uuid4(),
            model_type="Prophet",
            target_date=now + timedelta(days=30),
            projected_rate=6.5,
            confidence_upper=7.0,
            confidence_lower=6.0,
            generated_at=now
        )
        self.db.add(forecast)
        
        # Setup active rule
        rule = AlertRule(
            id=uuid.uuid4(),
            user_id=mock_user_id,
            rule_name="High Inflation Forecast",
            alert_type="threshold",
            indicator="projected_rate",
            condition_operator=">",
            threshold_value=6.0,
            horizon_days=30,
            email_channel=True,
            cooldown_hours=6.0,
            is_active=True,
            created_at=now
        )
        self.db.add(rule)
        self.db.commit()

        # Run evaluation engine
        res = AlertEvaluationEngine.run(self.db)
        self.assertEqual(res["rules_evaluated"], 1)
        self.assertEqual(res["rules_fired"], 1)

        # Assert notification was created in db
        notifs = self.db.query(AlertNotification).all()
        self.assertEqual(len(notifs), 1)
        self.assertEqual(notifs[0].alert_type, "threshold")
        self.assertEqual(notifs[0].trigger_value, 6.5)
        self.assertEqual(notifs[0].severity, "high")

    def test_rule_cooldown_execution(self):
        """Assert rule cooldown prevents subsequent triggers."""
        now = datetime.utcnow()
        # Setup Currency Shock data
        currency = CurrencyData(
            id=uuid.uuid4(),
            recording_date=now,
            usd_inr=83.5,
            eur_usd=1.08,
            brent_crude=92.0,
            gold_index=2000.0,
            brent_crude_shock_score=8.5  # breaching score
        )
        self.db.add(currency)

        # Setup rule
        rule = AlertRule(
            id=uuid.uuid4(),
            user_id=mock_user_id,
            rule_name="Oil Shock Score",
            alert_type="currency_shock",
            indicator="brent_crude_shock_score",
            condition_operator=">",
            threshold_value=7.0,
            cooldown_hours=6.0,
            is_active=True,
            created_at=now
        )
        self.db.add(rule)
        self.db.commit()

        # 1st run should fire
        res1 = AlertEvaluationEngine.run(self.db)
        self.assertEqual(res1["rules_fired"], 1)

        # 2nd run immediately after should not fire due to cooldown
        res2 = AlertEvaluationEngine.run(self.db)
        self.assertEqual(res2["rules_fired"], 0)

    def test_quiet_hours_suppression(self):
        """Assert quiet hours suppress notifications during configured hours."""
        now = datetime.utcnow()
        # Create active rule that would breach
        forecast = Forecast(
            id=uuid.uuid4(),
            model_type="Prophet",
            target_date=now + timedelta(days=30),
            projected_rate=6.5,
            confidence_upper=7.0,
            confidence_lower=6.0,
            generated_at=now
        )
        self.db.add(forecast)
        rule = AlertRule(
            id=uuid.uuid4(),
            user_id=mock_user_id,
            rule_name="High Inflation Forecast",
            alert_type="threshold",
            indicator="projected_rate",
            condition_operator=">",
            threshold_value=6.0,
            horizon_days=30,
            email_channel=True,
            cooldown_hours=6.0,
            is_active=True,
            created_at=now
        )
        self.db.add(rule)

        # Setup quiet hours that span the current time
        pref = UserNotificationPreference(
            id=uuid.uuid4(),
            user_id=mock_user_id,
            email_enabled=True,
            quiet_hours_start="00:00",
            quiet_hours_end="23:59",  # Covers all day
            quiet_hours_timezone="UTC"
        )
        self.db.add(pref)
        self.db.commit()

        # Run evaluation
        res = AlertEvaluationEngine.run(self.db)
        # Should not fire because user is in quiet hours
        self.assertEqual(res["rules_fired"], 0)

    def test_daily_alert_limits(self):
        """Assert daily alert limits suppress notifications when exceeded."""
        now = datetime.utcnow()
        pref = UserNotificationPreference(
            id=uuid.uuid4(),
            user_id=mock_user_id,
            email_enabled=True,
            daily_alert_limit=2
        )
        self.db.add(pref)

        # Setup 2 past notifications created today
        for _ in range(2):
            self.db.add(AlertNotification(
                id=uuid.uuid4(),
                user_id=mock_user_id,
                alert_type="threshold",
                severity="low",
                channel="email",
                body="Past alert body",
                status="sent",
                created_at=now - timedelta(hours=1)
            ))
        
        # Setup a new forecast breaching
        forecast = Forecast(
            id=uuid.uuid4(),
            model_type="Prophet",
            target_date=now + timedelta(days=30),
            projected_rate=6.5,
            confidence_upper=7.0,
            confidence_lower=6.0,
            generated_at=now
        )
        self.db.add(forecast)
        rule = AlertRule(
            id=uuid.uuid4(),
            user_id=mock_user_id,
            rule_name="High Inflation Forecast",
            alert_type="threshold",
            indicator="projected_rate",
            condition_operator=">",
            threshold_value=6.0,
            horizon_days=30,
            email_channel=True,
            cooldown_hours=6.0,
            is_active=True,
            created_at=now
        )
        self.db.add(rule)
        self.db.commit()

        # Run evaluation
        res = AlertEvaluationEngine.run(self.db)
        # Should suppress because daily limit (2) is already met
        self.assertEqual(res["rules_fired"], 0)

    def test_email_digest_aggregation(self):
        """Verify daily digests bundle multiple pending digest emails."""
        now = datetime.utcnow()
        # Setup user preference with daily digest enabled
        pref = UserNotificationPreference(
            id=uuid.uuid4(),
            user_id=mock_user_id,
            email_enabled=True,
            email_digest_mode="daily"
        )
        self.db.add(pref)

        # Enqueue 3 notifications with status pending_digest
        for i in range(3):
            self.db.add(AlertNotification(
                id=uuid.uuid4(),
                user_id=mock_user_id,
                alert_type="threshold",
                severity="medium",
                channel="email",
                subject=f"Threshold Alert {i}",
                body=f"Trigger {i} crossed threshold value.",
                status="pending_digest",
                created_at=now
            ))
        self.db.commit()

        # Run daily digests processing
        AlertEvaluationEngine.send_digests(self.db, "daily")

        # Assert notifications status updated to sent
        notifs = self.db.query(AlertNotification).filter(AlertNotification.user_id == mock_user_id).all()
        for n in notifs:
            self.assertEqual(n.status, "sent")
            self.assertIsNotNone(n.delivered_at)


if __name__ == "__main__":
    unittest.main()
