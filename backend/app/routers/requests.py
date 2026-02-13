from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_correlation_id, require_permission
from app.db import get_db
from app.models import PolicyScope, Request, RequestStatus
from app.schemas import RequestCreate, RequestResponse
from app.services.audit_service import log_event
from app.services.policy_service import evaluate_rules
from app.services.workflow_service import transition_allowed

router = APIRouter(prefix="/requests", tags=["requests"])


@router.post("", response_model=RequestResponse)
def create_request(
    payload: RequestCreate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("request:create")),
    correlation_id: str = Depends(get_correlation_id),
):
    context = {"request": payload.model_dump()}
    decision = evaluate_rules(db, user.tenant_id, PolicyScope.REQUEST_CREATE, context)
    if decision["final_decision"] == "BLOCK":
        raise HTTPException(status_code=409, detail=decision["reasons"])
    req = Request(tenant_id=user.tenant_id, **payload.model_dump())
    if decision["computed_fields"].get("sla_due_at"):
        req.sla_due_at = datetime.fromisoformat(decision["computed_fields"]["sla_due_at"])
    if decision["final_decision"] == "AUTO_APPROVE":
        req.status = RequestStatus.Approved
        req.approved_by_user_id = user.id
    db.add(req)
    db.flush()
    log_event(db, tenant_id=user.tenant_id, entity_type="Request", entity_id=req.id, action="REQUEST_CREATED", correlation_id=correlation_id, user_id=user.id, after={"status": req.status.value})
    db.commit()
    db.refresh(req)
    return req


@router.post("/{request_id}/transition/{target}", response_model=RequestResponse)
def transition_request(request_id: str, target: RequestStatus, db: Session = Depends(get_db), user=Depends(require_permission("request:approve")), correlation_id: str = Depends(get_correlation_id)):
    req = db.query(Request).filter_by(id=request_id, tenant_id=user.tenant_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Not found")
    if not transition_allowed(req.status, target):
        raise HTTPException(status_code=409, detail="Invalid transition")
    before = {"status": req.status.value}
    req.status = target
    db.flush()
    log_event(db, tenant_id=user.tenant_id, entity_type="Request", entity_id=req.id, action="STATUS_CHANGED", correlation_id=correlation_id, user_id=user.id, before=before, after={"status": req.status.value})
    db.commit()
    db.refresh(req)
    return req
