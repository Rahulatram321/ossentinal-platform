"""Single gateway for GitHub repository lookups."""
from github.fetcher import fetch_repo_data


class GitHubService:
    def repository(self, full_name: str, token: str = "") -> dict:
        return fetch_repo_data(full_name, token)
