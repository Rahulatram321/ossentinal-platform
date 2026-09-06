from datetime import datetime
from core.database import SessionLocal, TriageLog, PRReview
from sqlalchemy import func, select


def generate(repo_name: str) -> dict:
    db = SessionLocal()
    try:
        triaged = db.scalar(select(func.count(TriageLog.id)).where(TriageLog.repo_full_name == repo_name)) or 0
        reviewed = db.scalar(select(func.count(PRReview.id)).where(PRReview.repo_full_name == repo_name)) or 0
        urgent = db.scalar(select(func.count(TriageLog.id)).where(TriageLog.repo_full_name == repo_name, TriageLog.priority_level == "Urgent")) or 0
        markdown = f"## Weekly report for {repo_name}\n\n- Issues triaged: {triaged}\n- Pull requests reviewed: {reviewed}\n- Urgent issues: {urgent}\n\nGenerated {datetime.utcnow():%Y-%m-%d}."
        return {"markdown": markdown, "triaged_count": triaged, "reviewed_count": reviewed, "urgent_count": urgent}
    finally: db.close()
