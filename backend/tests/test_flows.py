import uuid

from fastapi.testclient import TestClient

from app.db import Base, SessionLocal, engine
from app.main import app
from app.models import AssetType, Location, OrganizationUnit, Tenant, User
from app.seed import run


client = TestClient(app)


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    run()
    db = SessionLocal()
    tenant = db.query(Tenant).first()
    db.add_all([
        OrganizationUnit(id=uuid.uuid4(), tenant_id=tenant.id, name="Ops"),
        AssetType(id=uuid.uuid4(), tenant_id=tenant.id, name="Item A", category="standard"),
        Location(id=uuid.uuid4(), tenant_id=tenant.id, name="Loc A"),
    ])
    db.commit()
    db.close()


def token():
    res = client.post('/auth/login', json={'email': 'admin@example.com', 'password': 'admin123'})
    return res.json()['access_token']


def test_request_create_event_logged():
    db = SessionLocal()
    ou = db.query(OrganizationUnit).first(); at = db.query(AssetType).first(); db.close()
    res = client.post('/requests', headers={'Authorization': f'Bearer {token()}', 'X-Correlation-Id': 'c1'}, json={'requester_unit_id': str(ou.id), 'asset_type_id': str(at.id), 'quantity': 10})
    assert res.status_code == 200


def test_policy_auto_approve_small_quantity():
    db = SessionLocal()
    ou = db.query(OrganizationUnit).first(); at = db.query(AssetType).first(); db.close()
    res = client.post('/requests', headers={'Authorization': f'Bearer {token()}'}, json={'requester_unit_id': str(ou.id), 'asset_type_id': str(at.id), 'quantity': 2})
    assert res.status_code == 200
    assert res.json()['status'] == 'Approved'


def test_execute_request_posts_transaction():
    db = SessionLocal()
    ou = db.query(OrganizationUnit).first(); at = db.query(AssetType).first(); loc = db.query(Location).first(); db.close()
    req = client.post('/requests', headers={'Authorization': f'Bearer {token()}'}, json={'requester_unit_id': str(ou.id), 'asset_type_id': str(at.id), 'quantity': 2}).json()
    tx = client.post('/transactions', headers={'Authorization': f'Bearer {token()}'}, json={'request_id': req['id'], 'type': 'IN', 'to_location_id': str(loc.id), 'asset_type_id': str(at.id), 'quantity': 2})
    assert tx.status_code == 200
