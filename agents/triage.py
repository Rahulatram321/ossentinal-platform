from agents.duplicate import find_duplicate
from agents.priority import calculate_priority
from core.config import settings


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
    response = _gemini(f"Classify this GitHub issue as exactly one of these three words: bug, feature, question. Title: {title}. Body: {body[:500]}. Reply with only the single classification word.")
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


def process_issue(repo_name: str, issue_number: int, title: str, body: str, token: str = "", open_issues=()) -> dict:
    label = classify_issue(title, body)
    duplicate = find_duplicate(f"{title} {body}", open_issues)
    priority = calculate_priority(label, f"{title} {body}", duplicate_similarity=duplicate["similarity"])
    reply = generate_reply(label, title, duplicate)
    return {"repo": repo_name, "issue_number": issue_number, "label": label, "duplicate": duplicate, "priority": priority, "reply": reply, "confidence": 0.86}
