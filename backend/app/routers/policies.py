from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import require_permission
from app.db import get_db
from app.models import PolicyScope
from app.schemas import PolicyTestRequest
from app.services.policy_service import evaluate_rules

router = APIRouter(prefix="/policies", tags=["policies"])


@router.post("/test")
def test_policy(payload: PolicyTestRequest, db: Session = Depends(get_db), user=Depends(require_permission("policy:test"))):
    return evaluate_rules(db, user.tenant_id, PolicyScope.REQUEST_CREATE, payload.model_dump())
