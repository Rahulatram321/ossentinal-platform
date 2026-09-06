import json
import re
import httpx
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
    return ""


def analyze_diff_with_gemini(diff: str) -> dict:
    return prism_fallback(diff)


def review_pr(url: str, token: str = "") -> dict:
    try:
        diff = fetch_pr_diff(url, token)
        return analyze_diff_with_gemini(diff) if diff else prism_fallback("")
    except Exception:
        return prism_fallback("")
