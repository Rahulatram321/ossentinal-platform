from pydantic import BaseModel, Field


class GitPulseQueryRequest(BaseModel):
    repo_name: str = Field(min_length=3, max_length=255)
    question: str = Field(min_length=3, max_length=4000)
