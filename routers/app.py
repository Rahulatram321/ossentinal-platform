from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from agents.gitpulse import answer_query
from agents.prism import review_pr
from agents.reports import generate
from agents.triage import process_issue
from core.database import SessionLocal, ConnectedRepo, TriageLog, PRReview, GitPulseQuery, WeeklyReport, get_user_stats, get_recent_logs, init_db
from core.security import get_session_token, is_authenticated, validate_csrf_token
from utils.logger import log_action
router = APIRouter(); templates = Jinja2Templates(directory="templates")

def user_id(request): return request.session.get("github_id", "demo")
def guard(request): return is_authenticated(request)

@router.get("/dashboard")
def dashboard(request: Request):
    if not guard(request): return RedirectResponse("/login", 303)
    db = SessionLocal(); repos = db.query(ConnectedRepo).filter_by(owner_github_id=user_id(request), is_active=True).all(); stats = get_user_stats(user_id(request), db); logs = get_recent_logs(user_id(request), db=db); db.close()
    return templates.TemplateResponse(request, "app/dashboard.html", {"stats": stats, "repos": repos, "logs": logs})

@router.get("/repos")
def repos(request: Request):
    if not guard(request): return RedirectResponse("/login", 303)
    db=SessionLocal(); rows=db.query(ConnectedRepo).filter_by(owner_github_id=user_id(request)).all(); db.close(); return templates.TemplateResponse(request, "app/repos.html", {"repos": rows})

@router.post("/repos/connect")
def connect(request: Request, repo_name: str = Form(...)):
    if not guard(request): return RedirectResponse("/login", 303)
    db=SessionLocal(); db.add(ConnectedRepo(owner_github_id=user_id(request), full_name=repo_name.strip(), webhook_status="active")); db.commit(); db.close(); return RedirectResponse("/dashboard", 303)

@router.get("/triage")
def triage(request: Request):
    if not guard(request): return RedirectResponse("/login", 303)
    db=SessionLocal(); rows=db.query(TriageLog).order_by(TriageLog.created_at.desc()).limit(100).all(); db.close(); return templates.TemplateResponse(request, "app/triage.html", {"rows": rows})

@router.get("/prism")
def prism(request: Request): return templates.TemplateResponse(request, "app/prism.html", {"result": None}) if guard(request) else RedirectResponse("/login", 303)

@router.post("/prism/review")
def prism_review(request: Request, pr_url: str = Form(...)):
    if not guard(request): return RedirectResponse("/login", 303)
    result=review_pr(pr_url, get_session_token(request)); return templates.TemplateResponse(request, "app/prism.html", {"result": result})

@router.get("/gitpulse")
def gitpulse(request: Request): return templates.TemplateResponse(request, "app/gitpulse.html", {"result": None}) if guard(request) else RedirectResponse("/login", 303)

@router.post("/gitpulse/query")
def gitpulse_query(request: Request, question: str = Form(...), repo_name: str = Form("demo/repo")):
    if not guard(request): return RedirectResponse("/login", 303)
    return templates.TemplateResponse(request, "app/gitpulse.html", {"result": answer_query(question, repo_name, get_session_token(request)), "repo_name": repo_name})

@router.get("/reports")
def reports(request: Request): return templates.TemplateResponse(request, "app/reports.html", {"reports": []}) if guard(request) else RedirectResponse("/login", 303)

@router.get("/settings")
def settings_page(request: Request): return templates.TemplateResponse(request, "app/settings.html", {}) if guard(request) else RedirectResponse("/login", 303)
