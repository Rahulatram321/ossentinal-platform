"""Durable triage work delegated from a verified GitHub webhook."""
from app.tasks.celery_app import celery_app
from app.services.triage_service import TriageService


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_jitter=True, retry_kwargs={"max_retries": 3})
def process_issue_triage(self, repo_name: str, issue_number: int, title: str, body: str) -> dict:
    return TriageService().process(repo_name, issue_number, title, body)
