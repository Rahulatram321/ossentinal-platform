import json
import re
import time
import httpx
from core.config import settings
from agents.fallbacks import prism_fallback


def parse_pr_url(url: str) -> tuple[str, str, int]:
    match = re.match(r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)", url.strip())
    if not match: raise ValueError("Enter a GitHub pull request URL")
    return match.group(1), match.group(2), int(match.group(3))


def fetch_pr_diff(url: str, token: str = "") -> str:
    owner, repo, number = parse_pr_url(url)
    headers = {"Accept": "application/vnd.github.v3.diff"}
    if token: headers["Authorization"] = f"Bearer {token}"
    for attempt in range(3):
        try:
            response = httpx.get(f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}", headers=headers, timeout=8)
            response.raise_for_status(); return response.text[:8000]
        except Exception:
            if attempt == 2: return ""
            time.sleep(0.5 * (2 ** attempt))
    return ""


def analyze_diff_with_gemini(diff: str) -> dict:
    truncated = diff[:8000]
    if not settings.gemini_api_key:
        return prism_fallback(truncated)
    prompt = """Review this pull-request diff. Return JSON only with quality_score (0-100), bug_risks (array), summary, suggested_reviewer, and improvement_tips (array).\n\nDIFF:\n""" + truncated
    for attempt in range(3):
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            text = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt).text.strip()
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
            data = json.loads(text)
            return {"quality_score": max(0, min(100, int(data.get("quality_score", 0)))), "bug_risks": list(data.get("bug_risks", [])),
                    "summary": str(data.get("summary", "")), "suggested_reviewer": str(data.get("suggested_reviewer", "")),
                    "improvement_tips": list(data.get("improvement_tips", [])), "offline_mode": False}
        except Exception:
            if attempt < 2:
                time.sleep(0.5 * (2 ** attempt))
    return prism_fallback(truncated)


def review_pr(url: str, token: str = "") -> dict:
    try:
        diff = fetch_pr_diff(url, token)
        return analyze_diff_with_gemini(diff) if diff else prism_fallback("")
    except Exception:
        return prism_fallback("")
