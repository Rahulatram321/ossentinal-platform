from fastapi import APIRouter, Depends
from app.dependencies import require_authenticated_user
from app.schemas.analytics import GitPulseQueryRequest
from app.services.gitpulse_service import GitPulseService

router = APIRouter(prefix="/api/v1/gitpulse", tags=["gitpulse"])


@router.post("/query")
def query_repository(payload: GitPulseQueryRequest, _: str = Depends(require_authenticated_user)) -> dict:
    return GitPulseService().answer(payload.question, payload.repo_name)
