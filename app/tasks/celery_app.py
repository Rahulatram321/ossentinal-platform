"""Celery application shared by workers and scheduled tasks."""
from celery import Celery
from app.config import settings

celery_app = Celery(
    "ossentinel",
    broker=settings.redis_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.triage_tasks", "app.tasks.report_tasks", "app.tasks.cleanup_tasks"],
)
celery_app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"], timezone="UTC", task_track_started=True)
