# Module: app.jobs.worker
# Description: Celery worker application instance configured with Redis broker targets.

from celery import Celery
from app.config import settings

celery_app = Celery(
    "inflation_iq_jobs",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.jobs.tasks"]
)

# Optional configuration adjustments
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
