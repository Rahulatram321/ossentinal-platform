from datetime import datetime, timedelta
from typing import Generator
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from core.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    github_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[str] = mapped_column(String(500), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    plan: Mapped[str] = mapped_column(String(30), default="free")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ConnectedRepo(Base):
    __tablename__ = "connected_repos"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_github_id: Mapped[str] = mapped_column(ForeignKey("users.github_id"), index=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    webhook_status: Mapped[str] = mapped_column(String(30), default="pending")
    total_triaged: Mapped[int] = mapped_column(Integer, default=0)
    total_reviewed: Mapped[int] = mapped_column(Integer, default=0)
    total_queries: Mapped[int] = mapped_column(Integer, default=0)
    connected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class TriageLog(Base):
    __tablename__ = "triage_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    repo_full_name: Mapped[str] = mapped_column(String(255), index=True)
    issue_number: Mapped[int] = mapped_column(Integer)
    issue_title: Mapped[str] = mapped_column(String(500))
    label: Mapped[str] = mapped_column(String(30))
    priority_score: Mapped[int] = mapped_column(Integer)
    priority_level: Mapped[str] = mapped_column(String(30))
    duplicate_warning: Mapped[bool] = mapped_column(Boolean, default=False)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.8)
    ai_reply_preview: Mapped[str] = mapped_column(String(200), default="")
    status: Mapped[str] = mapped_column(String(30), default="to_triage")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PRReview(Base):
    __tablename__ = "pr_reviews"
    id: Mapped[int] = mapped_column(primary_key=True)
    repo_full_name: Mapped[str] = mapped_column(String(255))
    pr_number: Mapped[int] = mapped_column(Integer, default=0)
    pr_url: Mapped[str] = mapped_column(String(500))
    quality_score: Mapped[int] = mapped_column(Integer)
    bug_risk_count: Mapped[int] = mapped_column(Integer, default=0)
    summary_preview: Mapped[str] = mapped_column(String(500), default="")
    suggested_reviewer: Mapped[str] = mapped_column(String(100), default="")
    offline_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class GitPulseQuery(Base):
    __tablename__ = "gitpulse_queries"
    id: Mapped[int] = mapped_column(primary_key=True)
    repo_full_name: Mapped[str] = mapped_column(String(255))
    question: Mapped[str] = mapped_column(Text)
    answer_preview: Mapped[str] = mapped_column(String(500), default="")
    chart_type: Mapped[str] = mapped_column(String(20), default="none")
    offline_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    repo_full_name: Mapped[str] = mapped_column(String(255))
    report_markdown: Mapped[str] = mapped_column(Text)
    triaged_count: Mapped[int] = mapped_column(Integer, default=0)
    reviewed_count: Mapped[int] = mapped_column(Integer, default=0)
    urgent_count: Mapped[int] = mapped_column(Integer, default=0)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    github_username: Mapped[str] = mapped_column(String(100), default="demo")
    module: Mapped[str] = mapped_column(String(30))
    action: Mapped[str] = mapped_column(String(255))
    repo_full_name: Mapped[str] = mapped_column(String(255), default="")
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(engine)


def get_user_stats(github_id: str, db=None) -> dict:
    session = db or SessionLocal()
    try:
        repos = session.scalars(select(ConnectedRepo).where(ConnectedRepo.owner_github_id == github_id, ConnectedRepo.is_active.is_(True))).all()
        names = [repo.full_name for repo in repos]
        triaged = session.scalar(select(func.count(TriageLog.id)).where(TriageLog.repo_full_name.in_(names))) if names else 0
        reviewed = session.scalar(select(func.count(PRReview.id)).where(PRReview.repo_full_name.in_(names))) if names else 0
        queries = session.scalar(select(func.count(GitPulseQuery.id)).where(GitPulseQuery.repo_full_name.in_(names))) if names else 0
        return {"triaged": triaged or 0, "reviewed": reviewed or 0, "queries": queries or 0, "health_score": 96 if names else 0, "repos_connected": len(repos)}
    finally:
        if db is None:
            session.close()


def get_recent_logs(github_id: str, limit: int = 50, db=None) -> list[dict]:
    session = db or SessionLocal()
    try:
        names = [repo.full_name for repo in session.scalars(select(ConnectedRepo).where(ConnectedRepo.owner_github_id == github_id)).all()]
        rows = session.scalars(select(ActivityLog).where(ActivityLog.repo_full_name.in_(names)).order_by(ActivityLog.created_at.desc()).limit(limit)).all() if names else []
        return [{"module": row.module, "action": row.action, "repo": row.repo_full_name, "created_at": row.created_at, "metadata": row.metadata_json} for row in rows]
    finally:
        if db is None:
            session.close()


def log_activity(module: str, action: str, username: str, repo: str = "", metadata: str = "{}", db=None) -> None:
    session = db or SessionLocal()
    try:
        session.add(ActivityLog(github_username=username, module=module, action=action, repo_full_name=repo, metadata_json=metadata))
        session.commit()
    finally:
        if db is None:
            session.close()


def seed_demo_data() -> None:
    """Create a small, useful first-run activity trail without duplicating it."""
    db = SessionLocal()
    try:
        if db.scalar(select(func.count(ActivityLog.id))) or 0:
            return
        db.add_all([
            ActivityLog(github_username="demo", module="triage", action="Demo workspace initialized", repo_full_name="demo/ossentinel"),
            ActivityLog(github_username="demo", module="prism", action="Ready to review pull requests", repo_full_name="demo/ossentinel"),
            ActivityLog(github_username="demo", module="gitpulse", action="Ready for repository questions", repo_full_name="demo/ossentinel"),
        ])
        db.commit()
    finally:
        db.close()
