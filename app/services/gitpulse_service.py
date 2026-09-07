"""Application service for repository analytics queries."""
from agents.gitpulse import answer_query


class GitPulseService:
    def answer(self, question: str, repo_name: str, token: str = "") -> dict:
        return answer_query(question, repo_name, token)
