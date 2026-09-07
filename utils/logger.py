import json
from datetime import datetime, timedelta
from pathlib import Path
from core.database import log_activity, SessionLocal, ActivityLog
from sqlalchemy import func, select


def log_action(entry: dict) -> None:
    try: log_activity(entry.get("module", "system"), entry.get("action", ""), entry.get("username", "demo"), entry.get("repo", ""), json.dumps(entry.get("metadata", {})))
    except Exception:
        path = Path("logs/fallback.json"); path.parent.mkdir(exist_ok=True)
        rows = json.loads(path.read_text()) if path.exists() else []
        rows.append(entry); path.write_text(json.dumps(rows, default=str))


def get_logs(limit=50) -> list[dict]:
    db = SessionLocal()
    try:
        rows = db.scalars(select(ActivityLog).order_by(ActivityLog.created_at.desc()).limit(limit)).all()
        return [{"module": r.module, "action": r.action, "repo": r.repo_full_name, "created_at": r.created_at} for r in rows]
    finally: db.close()


def get_stats() -> dict:
    db = SessionLocal()
    try:
        counts = {module: db.scalar(select(func.count(ActivityLog.id)).where(ActivityLog.module == module)) or 0 for module in ("triage", "prism", "gitpulse")}
        return {"total_triaged": counts["triage"], "total_reviewed": counts["prism"], "total_queries": counts["gitpulse"], "health_score": 96}
    finally: db.close()


def get_weekly_trend(username: str | None = None) -> list[int]:
    """Return counts oldest-to-newest for the last seven calendar days."""
    db = SessionLocal()
    try:
        today = datetime.utcnow().date()
        result = []
        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)
            statement = select(func.count(ActivityLog.id)).where(
                ActivityLog.created_at >= datetime.combine(day, datetime.min.time()),
                ActivityLog.created_at < datetime.combine(day + timedelta(days=1), datetime.min.time()),
            )
            if username:
                statement = statement.where(ActivityLog.github_username == username)
            result.append(db.scalar(statement) or 0)
        return result
    finally:
        db.close()
