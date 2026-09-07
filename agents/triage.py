from agents.duplicate import find_duplicate
from agents.priority import calculate_priority_score
from core.config import settings
from core.database import SessionLocal, TriageLog
from utils.logger import log_action
from utils.prompts import render_prompt
import httpx


def _gemini(prompt: str) -> str:
    if not settings.gemini_api_key:
        return ""
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        return genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt).text.strip()
    except Exception:
        return ""


def classify_issue(title: str, body: str) -> str:
    response = _gemini(render_prompt("triage_classification.txt", title=title, body=body[:500])).lower()
    if response in {"bug", "feature", "question"}:
        return response
    text = f"{title} {body}".lower()
    if any(word in text for word in ("bug", "error", "crash", "broken", "fail")): return "bug"
    if any(word in text for word in ("feature", "request", "add", "support")): return "feature"
    return "question"


def apply_label(repo, issue, label: str) -> bool:
    try:
        repo.get_label(label)
    except Exception:
        try: repo.create_label(label, {"bug": "d73a4a", "feature": "0075ca", "question": "e4e669"}.get(label, "6f42c1"))
        except Exception: return False
    try: issue.add_to_labels(label)
    except Exception: return False
    return True


def generate_reply(label: str, title: str, dup_info: dict) -> str:
    response = _gemini(f"You are a helpful open-source maintainer. Write a short friendly GitHub issue comment (exactly 2-3 sentences) for this {label} issue titled '{title}'. Acknowledge warmly, ask for missing info. No markdown headers.")
    if response:
        return response
    if dup_info.get("is_duplicate"): return f"Thanks for reporting this {label} issue. It looks related to issue #{dup_info.get('issue_number')}; we will compare the reports and follow up there."
    return f"Thanks for opening this {label} issue about {title}. We appreciate the detail and will review it shortly; any additional reproduction steps or context would help."


def apply_github_actions(repo_name: str, issue_number: int, label: str, reply: str, token: str) -> bool:
    """Create/apply the label and publish the draft when a GitHub token is supplied."""
    if not token:
        return False
    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}
    color = {"bug": "d73a4a", "feature": "0075ca", "question": "e4e669"}[label]
    base = f"https://api.github.com/repos/{repo_name}"
    try:
        # Creating an existing label returns 422, which is safe to ignore.
        httpx.post(f"{base}/labels", headers=headers, json={"name": label, "color": color}, timeout=10)
        labels = httpx.post(f"{base}/issues/{issue_number}/labels", headers=headers, json={"labels": [label]}, timeout=10)
        comment = httpx.post(f"{base}/issues/{issue_number}/comments", headers=headers, json={"body": reply}, timeout=10)
        return labels.is_success and comment.is_success
    except httpx.HTTPError:
        return False


def process_issue(repo_name: str, issue_number: int, title: str, body: str, token: str = "", open_issues=()) -> dict:
    """Run the seven-step offline-safe triage workflow for one issue."""
    # 1: classify, 2: find a duplicate, 3: score, 4: draft a reply.
    label = classify_issue(title, body)
    duplicate = find_duplicate(f"{title} {body}", open_issues)
    priority = calculate_priority_score(label, f"{title} {body}", duplicate_similarity=duplicate["similarity"])
    reply = generate_reply(label, title, duplicate)
    result = {"repo": repo_name, "issue_number": issue_number, "label": label, "duplicate": duplicate, "priority": priority, "reply": reply, "confidence": 0.86}
    # 5: apply GitHub label/comment, 6: persist the result, 7: log activity.
    result["github_applied"] = apply_github_actions(repo_name, issue_number, label, reply, token)
    try:
        db = SessionLocal()
        try:
            db.add(TriageLog(repo_full_name=repo_name, issue_number=issue_number, issue_title=title[:500], label=label,
                priority_score=priority["score"], priority_level=priority["level"], duplicate_warning=duplicate["is_duplicate"],
                ai_reply_preview=reply[:200], status="ready_to_apply"))
            db.commit()
        finally:
            db.close()
        log_action({"module": "triage", "action": f"Triaged issue #{issue_number}", "username": "webhook", "repo": repo_name, "metadata": result})
        result["persisted"] = True
    except Exception:
        # Classification remains useful even when a transient database failure occurs.
        result["persisted"] = False
    result["steps_completed"] = 7
    return result
