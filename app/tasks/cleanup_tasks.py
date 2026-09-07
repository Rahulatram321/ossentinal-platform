"""Retention task for future production log cleanup policies."""
from datetime import UTC, datetime, timedelta
from sqlalchemy import delete
from app.tasks.celery_app import celery_app
from core.database import ActivityLog, SessionLocal


@celery_app.task
def cleanup_old_logs(retention_days: int = 90) -> int:
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(days=retention_days)
    db = SessionLocal()
    try:
        result = db.execute(delete(ActivityLog).where(ActivityLog.created_at < cutoff))
        db.commit()
        return result.rowcount or 0
    finally:
        db.close()
