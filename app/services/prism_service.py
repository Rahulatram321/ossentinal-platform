"""Application service for PRism reviews."""
from agents.prism import review_pr


class PrismService:
    def analyze(self, pr_url: str, token: str = "") -> dict:
        return review_pr(pr_url, token)
