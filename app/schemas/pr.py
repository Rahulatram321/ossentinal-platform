from pydantic import BaseModel, HttpUrl


class PRAnalysisRequest(BaseModel):
    pr_url: HttpUrl
