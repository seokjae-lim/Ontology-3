import uuid

from app.core.security import hash_password
from app.db import SessionLocal
from app.models import Permission, PolicyRule, PolicyScope, Role, RolePermission, Tenant, User, UserOrgRole


def run():
    db = SessionLocal()
    tenant = db.query(Tenant).filter_by(name="DEFAULT Tenant").first() or Tenant(id=uuid.uuid4(), name="DEFAULT Tenant")
    db.add(tenant)
    db.flush()

    role_names = ["Admin", "Operator", "Requester", "Auditor"]
    roles = {}
    for name in role_names:
        role = db.query(Role).filter_by(name=name).first() or Role(name=name)
        db.add(role)
        db.flush()
        roles[name] = role

    perm_codes = ["request:create", "request:approve", "transaction:create", "policy:test", "import:asset-types", "import:locations", "generator:map", "generator:apply"]
    perms = {}
    for c in perm_codes:
        p = db.query(Permission).filter_by(code=c).first() or Permission(code=c)
        db.add(p)
        db.flush()
        perms[c] = p

    for p in perms.values():
        db.merge(RolePermission(role_id=roles["Admin"].id, permission_id=p.id))
    for c in ["request:create", "transaction:create", "request:approve"]:
        db.merge(RolePermission(role_id=roles["Operator"].id, permission_id=perms[c].id))
    db.merge(RolePermission(role_id=roles["Requester"].id, permission_id=perms["request:create"].id))

    admin = db.query(User).filter_by(email="admin@example.com").first()
    if not admin:
        admin = User(email="admin@example.com", password_hash=hash_password("admin123"), tenant_id=tenant.id)
        db.add(admin)
        db.flush()
        db.add(UserOrgRole(user_id=admin.id, role_id=roles["Admin"].id, tenant_id=tenant.id))

    if not db.query(PolicyRule).filter_by(name="Auto approve small quantity").first():
        db.add(PolicyRule(
            tenant_id=tenant.id,
            name="Auto approve small quantity",
            priority=100,
            enabled=True,
            scope=PolicyScope.REQUEST_CREATE,
            condition_json={"op": "lte", "field": "request.quantity", "value": 5},
            action_json={"type": "AUTO_APPROVE"},
        ))
    db.commit()
    db.close()


if __name__ == "__main__":
    run()
