from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from agents.prism import review_pr
from agents.triage import process_issue
from core.database import SessionLocal, TriageLog, PRReview, GitPulseQuery, get_user_stats
from core.security import get_session_token, is_authenticated
from utils.logger import get_weekly_trend
router = APIRouter(prefix="/api/v1")

class TriageRequest(BaseModel): repo: str; issue_number: int; title: str; body: str = ""
class PrismRequest(BaseModel): pr_url: str

def auth(request): return is_authenticated(request)

@router.get("/health")
def api_health(): return {"status": "ok", "modules": {"triage": True, "prism": True, "gitpulse": True}}

@router.get("/stats")
def stats(request: Request):
    if not auth(request): return JSONResponse({"detail": "unauthorized"}, 401)
    data = get_user_stats(request.session.get("github_id", "demo"))
    data["weekly_trend"] = get_weekly_trend(request.session.get("github_username"))
    return data

@router.get("/repos")
def repo_list(request: Request):
    if not auth(request): return JSONResponse({"detail": "unauthorized"}, 401)
    db=SessionLocal(); rows=db.query(__import__("core.database", fromlist=["ConnectedRepo"]).ConnectedRepo).filter_by(owner_github_id=request.session.get("github_id", "demo")).all(); db.close(); return [{"name": r.full_name, "active": r.is_active, "triaged": r.total_triaged} for r in rows]

@router.get("/triage/recent")
def recent_triage(request: Request, limit: int = 20):
    if not auth(request): return JSONResponse({"detail": "unauthorized"}, 401)
    db=SessionLocal(); rows=db.query(TriageLog).order_by(TriageLog.created_at.desc()).limit(min(limit, 100)).all(); db.close(); return [{"issue": r.issue_number, "title": r.issue_title, "label": r.label, "priority": r.priority_level} for r in rows]

@router.get("/prism/recent")
def recent_prism(request: Request, limit: int = 20):
    if not auth(request): return JSONResponse({"detail": "unauthorized"}, 401)
    db=SessionLocal(); rows=db.query(PRReview).order_by(PRReview.created_at.desc()).limit(min(limit, 100)).all(); db.close(); return [{"url": r.pr_url, "score": r.quality_score} for r in rows]

@router.post("/triage")
def triage(request: Request, payload: TriageRequest):
    if not auth(request): return JSONResponse({"detail": "unauthorized"}, 401)
    return process_issue(payload.repo, payload.issue_number, payload.title, payload.body, get_session_token(request) or "")

@router.post("/prism")
def prism(request: Request, payload: PrismRequest):
    if not auth(request): return JSONResponse({"detail": "unauthorized"}, 401)
    return review_pr(payload.pr_url, get_session_token(request) or "")
