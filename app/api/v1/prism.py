from fastapi import APIRouter, Depends
from app.dependencies import require_authenticated_user
from app.schemas.pr import PRAnalysisRequest
from app.services.prism_service import PrismService

router = APIRouter(prefix="/api/v1/prism", tags=["prism"])


@router.post("/analyze")
def analyze_pull_request(payload: PRAnalysisRequest, _: str = Depends(require_authenticated_user)) -> dict:
    return PrismService().analyze(str(payload.pr_url))
