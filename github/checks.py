import httpx


def publish_check(repo_name: str, sha: str, conclusion: str, title: str, summary: str, token: str = "") -> bool:
    """Publish a completed GitHub check run when a repository token is available."""
    if not token or not repo_name or not sha:
        return False
    headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"}
    payload = {"name": "OSSentinel", "head_sha": sha, "status": "completed", "conclusion": conclusion,
               "output": {"title": title[:255], "summary": summary[:65535]}}
    try:
        response = httpx.post(f"https://api.github.com/repos/{repo_name}/check-runs", headers=headers, json=payload, timeout=10)
        return response.is_success
    except httpx.HTTPError:
        return False
