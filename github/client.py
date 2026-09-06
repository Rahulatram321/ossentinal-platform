import httpx


def get_repo(repo_name: str, token: str = "") -> dict | None:
    headers = {"Accept": "application/vnd.github+json"}
    if token: headers["Authorization"] = f"Bearer {token}"
    try:
        response = httpx.get(f"https://api.github.com/repos/{repo_name}", headers=headers, timeout=8)
        return response.json() if response.is_success else None
    except Exception: return None
