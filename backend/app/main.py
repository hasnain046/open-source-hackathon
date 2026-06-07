# Module: app.main
# Description: Main application entry point for the InflationIQ FastAPI backend.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API services supporting AI forecasts, CPI analytics, news sentiment, and policy simulator runs.",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to actual domains in production configurations
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

# APScheduler Setup
from apscheduler.schedulers.background import BackgroundScheduler
from app.jobs.tasks import evaluate_alarm_triggers, send_pending_notifications, send_daily_digests, send_weekly_digests

scheduler = BackgroundScheduler()

def start_alert_scheduler():
    # Evaluate rules
    scheduler.add_job(
        evaluate_alarm_triggers,
        "interval",
        minutes=settings.ALERT_EVAL_INTERVAL_MINUTES,
        id="evaluate_alert_rules"
    )
    # Send pending
    scheduler.add_job(
        send_pending_notifications,
        "interval",
        minutes=5,
        id="send_pending_notifications"
    )
    # Daily digests at 12:30 UTC
    scheduler.add_job(
        send_daily_digests,
        "cron",
        hour=12,
        minute=30,
        id="send_daily_digests"
    )
    # Weekly digests at Sunday 12:30 UTC
    scheduler.add_job(
        send_weekly_digests,
        "cron",
        day_of_week="sun",
        hour=12,
        minute=30,
        id="send_weekly_digests"
    )
    scheduler.start()

def stop_alert_scheduler():
    scheduler.shutdown()

app.add_event_handler("startup", start_alert_scheduler)
app.add_event_handler("shutdown", stop_alert_scheduler)

@app.get("/")
def read_root():
    return {
        "status": "Operational",
        "service": settings.PROJECT_NAME,
        "api_version": "v1"
    }

