from sqlalchemy.orm import Session

from app.models import EventLog


def log_event(db: Session, *, tenant_id, entity_type: str, entity_id, action: str, correlation_id: str, user_id=None, before=None, after=None, metadata=None):
    event = EventLog(
        tenant_id=tenant_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        correlation_id=correlation_id,
        user_id=user_id,
        before_json=before,
        after_json=after,
        metadata=metadata,
    )
    db.add(event)
