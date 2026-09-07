from pydantic import BaseModel, Field


class TriageRequest(BaseModel):
    repo: str = Field(min_length=3, max_length=255)
    issue_number: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=500)
    body: str = ""
