# Module: app.jobs.tasks
# Description: Background job task definitions for scheduled pipelines.

from app.jobs.worker import celery_app
from app.core.database import SessionLocal
from app.services.alert_service import AlertEvaluationEngine

@celery_app.task(name="tasks.run_data_ingestion_pipeline")
def run_data_ingestion_pipeline():
    """Trigger FRED, BLS, and GDELT ETL processes in the background."""
    pass


@celery_app.task(name="tasks.evaluate_alarm_triggers")
def evaluate_alarm_triggers():
    """Validate recent values against user rules and dispatch notifications."""
    db = SessionLocal()
    try:
        res = AlertEvaluationEngine.run(db)
        return res
    finally:
        db.close()


@celery_app.task(name="tasks.send_pending_notifications")
def send_pending_notifications():
    """Process enqueued failed/retrying notifications with backoff."""
    db = SessionLocal()
    try:
        AlertEvaluationEngine.send_pending_notifications(db)
    finally:
        db.close()


@celery_app.task(name="tasks.send_daily_digests")
def send_daily_digests():
    """Aggregate daily digest notifications and send consolidated email."""
    db = SessionLocal()
    try:
        AlertEvaluationEngine.send_digests(db, "daily")
    finally:
        db.close()


@celery_app.task(name="tasks.send_weekly_digests")
def send_weekly_digests():
    """Aggregate weekly digest notifications and send consolidated email."""
    db = SessionLocal()
    try:
        AlertEvaluationEngine.send_digests(db, "weekly")
    finally:
        db.close()


@celery_app.task(name="tasks.retrain_macro_forecasters")
def retrain_macro_forecasters():
    """Trigger model fitting scripts asynchronously."""
    pass
