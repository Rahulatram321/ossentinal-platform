from fastapi import APIRouter, BackgroundTasks, Header, Request
from fastapi.responses import JSONResponse
from github.webhook import parse_payload, validate_signature
from utils.queue import enqueue
router = APIRouter()

def queue_issue(payload: dict) -> None:
    issue = payload.get("issue", {})
    enqueue({"repo": payload.get("repository", {}).get("full_name", ""), "number": issue.get("number"), "title": issue.get("title", ""), "body": issue.get("body", "")})

@router.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks, x_github_event: str = Header(""), x_hub_signature_256: str | None = Header(None)):
    body = await request.body()
    if not validate_signature(body, x_hub_signature_256): return JSONResponse({"detail": "invalid signature"}, 401)
    try:
        payload = parse_payload(body)
    except (ValueError, TypeError):
        return JSONResponse({"detail": "invalid JSON payload"}, 400)
    if x_github_event == "issues" and payload.get("action") == "opened":
        background_tasks.add_task(queue_issue, payload)
        return {"status": "received"}
    if x_github_event == "pull_request" and payload.get("action") == "opened": return {"status": "received"}
    return {"status": "ignored"}
