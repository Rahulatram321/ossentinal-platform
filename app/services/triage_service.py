"""Application service for the OSSentinel issue-triage workflow."""
from agents.triage import process_issue


class TriageService:
    def process(self, repo_name: str, issue_number: int, title: str, body: str, token: str = "", open_issues=()) -> dict:
        return process_issue(repo_name, issue_number, title, body, token, open_issues)
