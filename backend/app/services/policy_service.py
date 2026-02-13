from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import PolicyRule, PolicyScope


def _field(context: dict, path: str):
    cur = context
    for p in path.split('.'):
        cur = cur.get(p, None) if isinstance(cur, dict) else None
    return cur


def _eval(cond: dict, context: dict) -> bool:
    if "and" in cond:
        return all(_eval(c, context) for c in cond["and"])
    if "or" in cond:
        return any(_eval(c, context) for c in cond["or"])
    if "not" in cond:
        return not _eval(cond["not"], context)
    op = cond.get("op")
    left = _field(context, cond.get("field", ""))
    right = cond.get("value")
    if op == "gt":
        return left > right
    if op == "gte":
        return left >= right
    if op == "lt":
        return left < right
    if op == "lte":
        return left <= right
    if op == "equals":
        return left == right
    if op == "in":
        return left in right
    if op == "exists":
        return left is not None
    return False


def evaluate_rules(db: Session, tenant_id, scope: PolicyScope, context: dict):
    rules = db.query(PolicyRule).filter_by(tenant_id=tenant_id, scope=scope, enabled=True).order_by(PolicyRule.priority.desc()).all()
    fired, reasons, actions = [], [], []
    decision = "ALLOW"
    computed = {}
    for r in rules:
        if _eval(r.condition_json, context):
            fired.append(r.name)
            action = r.action_json
            actions.append(action)
            if action.get("type") == "BLOCK":
                decision = "BLOCK"
                reasons.append(action.get("reason", "Blocked by policy"))
            if action.get("type") == "SET_SLA":
                computed["sla_due_at"] = (datetime.now(timezone.utc) + timedelta(hours=action.get("hours", 24))).isoformat()
            if action.get("type") == "AUTO_APPROVE" and decision != "BLOCK":
                decision = "AUTO_APPROVE"
    return {"fired_rules": fired, "reasons": reasons, "final_decision": decision, "actions": actions, "computed_fields": computed}
