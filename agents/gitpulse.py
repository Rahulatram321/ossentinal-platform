from agents.fallbacks import gitpulse_fallback


def fetch_repo_data(repo_name: str, token: str = "") -> str:
    return f"REPO INFO: {repo_name} | Stars: 0 | Forks: 0 | Open Issues: 0 | Language: Unknown"


def query_gemini(question: str, context: str) -> dict:
    return gitpulse_fallback(question)


def answer_query(question: str, repo_name: str, token: str = "") -> dict:
    try: return query_gemini(question, fetch_repo_data(repo_name, token))
    except Exception: return gitpulse_fallback(question)
