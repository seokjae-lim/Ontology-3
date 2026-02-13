from fastapi import Depends, Header, HTTPException
from jose import jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.models import Permission, RolePermission, User, UserOrgRole


def get_correlation_id(x_correlation_id: str | None = Header(default=None)) -> str:
    return x_correlation_id or "generated-correlation-id"


def get_current_user(db: Session = Depends(get_db), authorization: str | None = Header(default=None)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    token = authorization.split()[1]
    payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    user = db.query(User).filter_by(id=payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


def require_permission(code: str):
    def _dep(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        role_ids = [r.role_id for r in db.query(UserOrgRole).filter_by(user_id=user.id, tenant_id=user.tenant_id).all()]
        if not role_ids:
            raise HTTPException(status_code=403, detail="Forbidden")
        ok = (
            db.query(Permission)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .filter(RolePermission.role_id.in_(role_ids), Permission.code == code)
            .first()
        )
        if not ok:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return _dep
