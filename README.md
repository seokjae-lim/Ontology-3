# U-OIP (Universal Ontology-based Operational Intelligence Platform)

## DECISIONS NEEDED (with DEFAULTS used)
1. Deployment target (DEFAULT: Docker Compose local + optional cloud later).
2. Multi-tenant isolation strategy (DEFAULT: row-level `tenant_id` checks in services/dependencies).
3. Auth/session strategy (DEFAULT: JWT access token; refresh endpoint is DECISION NEEDED extension).
4. Notification integrations (DEFAULT: placeholder action only).
5. Workflow overrides by tenant (DEFAULT: canonical FSM with Approved->Cancelled allowed).
6. Materialized view refresh scheduler (DEFAULT: manual endpoint/stub; no cron deployed).
7. Import validation strictness (DEFAULT: required minimal columns, row-level error capture).
8. Generator mapping confidence threshold (DEFAULT: accept all proposals, confidence attached).
9. AI provider choice (DEFAULT: design-only stubs, no external model dependency).
10. Frontend charting library (DEFAULT: placeholders, no chart dependency).

## Architecture
- Backend: FastAPI + SQLAlchemy + Alembic + Postgres.
- Frontend: Next.js App Router (TypeScript) page scaffolds.
- Security: bcrypt hashing, JWT, permission dependency checks.
- Auditability: EventLog with correlation id on state changes.

## Core model
Implemented canonical entities: Tenant, User, Role, Permission, RolePermission, UserOrgRole, AssetType, Location, OrganizationUnit, Asset, Request, Transaction, PolicyRule, EventLog, LabelMap.

Ledger view:
- `inventory_balance_v` created by migration.

## RBAC matrix (seed)
- Admin: all seeded permissions.
- Operator: request:create, request:approve, transaction:create.
- Requester: request:create.
- Auditor: read-only endpoints (DECISION NEEDED extension for explicit read perms).

## Policy engine DSL
Supports logical operators (`and`,`or`,`not`) + comparisons (`equals`,`in`,`gt`,`gte`,`lt`,`lte`,`exists`) using field paths.
Actions: `AUTO_APPROVE`, `BLOCK`, `SET_SLA`, `NOTIFY` (placeholder), `REQUIRE_APPROVER_ROLE` (extension).

## 10 sample policy intents
1) Auto approve small quantity (seeded)
2) Block restricted category without admin
3) Short SLA for urgent purpose
4) Block on insufficient balance
5) Restrict requester role tags
6) Capacity checks for IN/MOVE
7) Time-window restrictions
8) Max outstanding requests per unit
9) Require approver role above threshold
10) Notify auditor on large MOVE

## Generator mode
- `POST /generator/map-schema` accepts headers/DDL/sample JSON and returns canonical mapping + confidence.
- `POST /generator/apply-domain-pack` applies domain pack skeleton.

Domain pack shape:
```json
{
  "labels": {"ASSET": "Equipment"},
  "assetTypes": [{"name": "Item A", "category": "standard"}],
  "policies": [],
  "workflowOverrides": {},
  "metadataSchemas": {}
}
```

## Run locally
```bash
cp .env.example .env
make up
```

## Useful commands
```bash
make migrate
make seed
make test
make down
```

## Seed user
- admin@example.com / admin123

## Demo script (curl)
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/auth/login -H 'content-type: application/json' -d '{"email":"admin@example.com","password":"admin123"}' | jq -r .access_token)

# Create request
curl -s -X POST http://localhost:8000/requests \
 -H "Authorization: Bearer $TOKEN" -H "X-Correlation-Id: req-1" -H 'content-type: application/json' \
 -d '{"requester_unit_id":"<uuid>","asset_type_id":"<uuid>","quantity":2}'

# Test policy evaluator
curl -s -X POST http://localhost:8000/policies/test \
 -H "Authorization: Bearer $TOKEN" -H 'content-type: application/json' \
 -d '{"request":{"quantity":2}}'

# Import asset types CSV
curl -s -X POST http://localhost:8000/import/asset-types \
 -H "Authorization: Bearer $TOKEN" -F file=@asset_types.csv
```

## Frontend pages
`/login`, `/dashboard`, `/assets`, `/asset-types`, `/locations`, `/requests`, `/transactions`, `/policies`, `/reports`, `/admin`.

## Testing critical flows
- request creation and event emission
- policy auto-approve for small quantity
- execution via transaction posting and status progression
