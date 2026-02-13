from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models import RequestStatus, TransactionType


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RequestCreate(BaseModel):
    requester_unit_id: UUID
    asset_type_id: UUID
    quantity: float
    purpose: str | None = None


class RequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    status: RequestStatus
    quantity: float
    sla_due_at: datetime | None


class TransactionCreate(BaseModel):
    request_id: UUID | None = None
    type: TransactionType
    from_location_id: UUID | None = None
    to_location_id: UUID | None = None
    asset_type_id: UUID
    quantity: float


class PolicyTestRequest(BaseModel):
    request: dict
    user: dict = {}
    assetType: dict = {}


class CSVImportResult(BaseModel):
    success_count: int
    fail_count: int
    row_errors: list[dict]


class GeneratorMapRequest(BaseModel):
    headers: list[str] = []
    sample_json: dict | None = None
    ddl: str | None = None
