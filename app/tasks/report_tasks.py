"""Scheduled weekly report generation."""
from agents.reports import generate
from app.tasks.celery_app import celery_app


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def generate_weekly_report(self, repo_name: str) -> dict:
    return generate(repo_name)
