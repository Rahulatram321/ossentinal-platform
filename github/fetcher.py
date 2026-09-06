from github.client import get_repo


def fetch_repo_data(repo_name: str, token: str = "") -> dict:
    return get_repo(repo_name, token) or {"full_name": repo_name, "stargazers_count": 0, "forks_count": 0, "open_issues_count": 0}
