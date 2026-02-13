from sqlalchemy import text
from sqlalchemy.orm import Session


def balance(db: Session, tenant_id, location_id, asset_type_id) -> float:
    q = text("""
    SELECT COALESCE(SUM(delta),0) FROM (
      SELECT CASE WHEN type='IN' THEN quantity WHEN type='ADJUST' THEN quantity ELSE 0 END as delta
      FROM transactions WHERE tenant_id=:tenant AND to_location_id=:loc AND asset_type_id=:asset
      UNION ALL
      SELECT CASE WHEN type IN ('OUT','MOVE') THEN -quantity ELSE 0 END as delta
      FROM transactions WHERE tenant_id=:tenant AND from_location_id=:loc AND asset_type_id=:asset
    ) x
    """)
    return float(db.execute(q, {"tenant": tenant_id, "loc": location_id, "asset": asset_type_id}).scalar() or 0)


def ensure_sufficient(db: Session, tenant_id, from_location_id, asset_type_id, quantity):
    if from_location_id is None:
        return
    if balance(db, tenant_id, from_location_id, asset_type_id) < quantity:
        raise ValueError("Insufficient balance")
