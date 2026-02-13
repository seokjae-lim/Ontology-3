from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_correlation_id, require_permission
from app.db import get_db
from app.models import Request, RequestStatus, Transaction, TransactionType
from app.schemas import TransactionCreate
from app.services.audit_service import log_event
from app.services.inventory_service import ensure_sufficient

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("")
def post_transaction(payload: TransactionCreate, db: Session = Depends(get_db), user=Depends(require_permission("transaction:create")), correlation_id: str = Depends(get_correlation_id)):
    if payload.type in [TransactionType.IN, TransactionType.OUT, TransactionType.MOVE] and payload.quantity <= 0:
        raise HTTPException(status_code=422, detail="Quantity must be > 0")
    if payload.type in [TransactionType.OUT, TransactionType.MOVE]:
        try:
            ensure_sufficient(db, user.tenant_id, payload.from_location_id, payload.asset_type_id, payload.quantity)
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc))
    tx = Transaction(tenant_id=user.tenant_id, approved_by_user_id=user.id, **payload.model_dump())
    db.add(tx)
    if payload.request_id:
        req = db.query(Request).filter_by(id=payload.request_id, tenant_id=user.tenant_id).first()
        if req and req.status == RequestStatus.Approved:
            req.status = RequestStatus.Executed
    db.flush()
    log_event(db, tenant_id=user.tenant_id, entity_type="Transaction", entity_id=tx.id, action="TRANSACTION_POSTED", correlation_id=correlation_id, user_id=user.id, after={"type": tx.type.value, "quantity": float(tx.quantity)})
    db.commit()
    return {"id": str(tx.id)}
