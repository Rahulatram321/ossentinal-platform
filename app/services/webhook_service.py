"""Webhook normalization used by HTTP delivery handlers and task dispatchers."""
from dataclasses import dataclass


@dataclass(frozen=True)
class IssueWebhook:
    repo_name: str
    issue_number: int
    title: str
    body: str


def parse_opened_issue(payload: dict) -> IssueWebhook | None:
    issue = payload.get("issue") or {}
    repository = payload.get("repository") or {}
    if not repository.get("full_name") or not issue.get("number"):
        return None
    return IssueWebhook(repository["full_name"], issue["number"], issue.get("title", ""), issue.get("body") or "")
