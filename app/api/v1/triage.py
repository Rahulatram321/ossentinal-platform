from fastapi import APIRouter, Depends
from app.dependencies import require_authenticated_user
from app.schemas.triage import TriageRequest
from app.services.triage_service import TriageService

router = APIRouter(prefix="/api/v1/triage", tags=["triage"])


@router.post("")
def triage_issue(payload: TriageRequest, _: str = Depends(require_authenticated_user)) -> dict:
    return TriageService().process(payload.repo, payload.issue_number, payload.title, payload.body)
