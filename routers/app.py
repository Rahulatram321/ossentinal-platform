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
from utils.rate_limit import allowed
router = APIRouter(); templates = Jinja2Templates(directory="templates")

def user_id(request): return request.session.get("github_id", "demo")
def guard(request): return is_authenticated(request)
def csrf_ok(request, token: str) -> bool: return validate_csrf_token(request.session, token)
def csrf_context(request):
    from core.security import issue_csrf_token
    return {"csrf_token": issue_csrf_token(request.session)}

@router.get("/dashboard")
def dashboard(request: Request):
    if not guard(request): return RedirectResponse("/login", 303)
    db = SessionLocal(); repos = db.query(ConnectedRepo).filter_by(owner_github_id=user_id(request), is_active=True).all(); stats = get_user_stats(user_id(request), db); logs = get_recent_logs(user_id(request), db=db); db.close()
    from utils.logger import get_weekly_trend
    return templates.TemplateResponse(request, "app/dashboard.html", {"stats": stats, "repos": repos, "logs": logs, "weekly_trend": get_weekly_trend(request.session.get("github_username")), **csrf_context(request)})

@router.get("/repos")
def repos(request: Request):
    if not guard(request): return RedirectResponse("/login", 303)
    db=SessionLocal(); rows=db.query(ConnectedRepo).filter_by(owner_github_id=user_id(request)).all(); db.close(); return templates.TemplateResponse(request, "app/repos.html", {"repos": rows, **csrf_context(request)})

@router.post("/repos/connect")
def connect(request: Request, repo_name: str = Form(...), csrf_token: str = Form("")):
    if not guard(request): return RedirectResponse("/login", 303)
    if not csrf_ok(request, csrf_token): return RedirectResponse("/repos?error=csrf", 303)
    name = repo_name.strip()
    if "/" not in name or len(name.split("/", 1)[0]) == 0 or len(name.split("/", 1)[1]) == 0: return RedirectResponse("/repos?error=invalid_repo", 303)
    db=SessionLocal()
    try:
        if not db.query(ConnectedRepo).filter_by(owner_github_id=user_id(request), full_name=name).one_or_none(): db.add(ConnectedRepo(owner_github_id=user_id(request), full_name=name, webhook_status="active"))
        db.commit()
    finally: db.close()
    log_action({"module": "repos", "action": "Connected repository", "username": request.session.get("github_username", "demo"), "repo": name})
    return RedirectResponse("/dashboard", 303)

@router.get("/triage")
def triage(request: Request):
    if not guard(request): return RedirectResponse("/login", 303)
    db=SessionLocal(); rows=db.query(TriageLog).order_by(TriageLog.created_at.desc()).limit(100).all(); db.close(); return templates.TemplateResponse(request, "app/triage.html", {"rows": rows, **csrf_context(request)})

@router.get("/prism")
def prism(request: Request): return templates.TemplateResponse(request, "app/prism.html", {"result": None, **csrf_context(request)}) if guard(request) else RedirectResponse("/login", 303)

@router.post("/prism/review")
def prism_review(request: Request, pr_url: str = Form(...), csrf_token: str = Form("")):
    if not guard(request): return RedirectResponse("/login", 303)
    if not csrf_ok(request, csrf_token): return RedirectResponse("/prism?error=csrf", 303)
    if not allowed(f"prism:{user_id(request)}", 10): return RedirectResponse("/prism?error=rate_limit", 303)
    result=review_pr(pr_url, get_session_token(request))
    db = SessionLocal()
    try:
        db.add(PRReview(repo_full_name="", pr_url=pr_url, quality_score=result["quality_score"], bug_risk_count=len(result["bug_risks"]), summary_preview=result["summary"][:500], suggested_reviewer=result.get("suggested_reviewer", ""), offline_mode=result.get("offline_mode", False))); db.commit()
    finally: db.close()
    log_action({"module": "prism", "action": "Reviewed pull request", "username": request.session.get("github_username", "demo")}); return templates.TemplateResponse(request, "app/prism.html", {"result": result, **csrf_context(request)})

@router.get("/gitpulse")
def gitpulse(request: Request): return templates.TemplateResponse(request, "app/gitpulse.html", {"result": None, **csrf_context(request)}) if guard(request) else RedirectResponse("/login", 303)

@router.post("/gitpulse/query")
def gitpulse_query(request: Request, question: str = Form(...), repo_name: str = Form("demo/repo"), csrf_token: str = Form("")):
    if not guard(request): return RedirectResponse("/login", 303)
    if not csrf_ok(request, csrf_token): return RedirectResponse("/gitpulse?error=csrf", 303)
    if not allowed(f"gitpulse:{user_id(request)}", 5): return RedirectResponse("/gitpulse?error=rate_limit", 303)
    result = answer_query(question, repo_name, get_session_token(request))
    db = SessionLocal()
    try:
        db.add(GitPulseQuery(repo_full_name=repo_name, question=question, answer_preview=result["answer"][:500], chart_type=result["chart_type"], offline_mode=result.get("offline_mode", False))); db.commit()
    finally: db.close()
    log_action({"module": "gitpulse", "action": "Answered repository question", "username": request.session.get("github_username", "demo"), "repo": repo_name}); return templates.TemplateResponse(request, "app/gitpulse.html", {"result": result, "repo_name": repo_name, **csrf_context(request)})

@router.get("/reports")
def reports(request: Request): return templates.TemplateResponse(request, "app/reports.html", {"reports": []}) if guard(request) else RedirectResponse("/login", 303)

@router.get("/settings")
def settings_page(request: Request): return templates.TemplateResponse(request, "app/settings.html", csrf_context(request)) if guard(request) else RedirectResponse("/login", 303)
