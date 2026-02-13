"""init

Revision ID: 0001
Revises:
Create Date: 2026-02-13
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('tenants', sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True), sa.Column('name', sa.String(100), unique=True), sa.Column('created_at', sa.DateTime(timezone=True)), sa.Column('updated_at', sa.DateTime(timezone=True)))
    # Lightweight bootstrap: create all tables from metadata for local dev
    bind = op.get_bind()
    from app.db import Base
    from app import models  # noqa: F401
    Base.metadata.create_all(bind)
    op.execute("""
    CREATE OR REPLACE VIEW inventory_balance_v AS
    SELECT tenant_id, asset_type_id, location_id, SUM(delta) AS balance
    FROM (
      SELECT tenant_id, asset_type_id, to_location_id AS location_id,
             CASE WHEN type='IN' THEN quantity WHEN type='MOVE' THEN quantity WHEN type='ADJUST' THEN quantity ELSE 0 END AS delta
      FROM transactions WHERE to_location_id IS NOT NULL
      UNION ALL
      SELECT tenant_id, asset_type_id, from_location_id AS location_id,
             CASE WHEN type='OUT' THEN -quantity WHEN type='MOVE' THEN -quantity ELSE 0 END AS delta
      FROM transactions WHERE from_location_id IS NOT NULL
    ) s GROUP BY tenant_id, asset_type_id, location_id;
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS inventory_balance_v")
    from app.db import Base
    bind = op.get_bind()
    Base.metadata.drop_all(bind)
