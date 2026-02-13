import csv
import io

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.deps import require_permission
from app.db import get_db
from app.models import AssetType, Location
from app.schemas import CSVImportResult

router = APIRouter(prefix="/import", tags=["import"])


@router.post("/asset-types", response_model=CSVImportResult)
async def import_asset_types(file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(require_permission("import:asset-types"))):
    text = (await file.read()).decode()
    rows = csv.DictReader(io.StringIO(text))
    ok, errors = 0, []
    for idx, row in enumerate(rows, start=2):
        try:
            db.add(AssetType(tenant_id=user.tenant_id, name=row["name"], category=row.get("category")))
            ok += 1
        except Exception as exc:  # noqa: PERF203
            errors.append({"row": idx, "error": str(exc)})
    db.commit()
    return CSVImportResult(success_count=ok, fail_count=len(errors), row_errors=errors)


@router.post("/locations", response_model=CSVImportResult)
async def import_locations(file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(require_permission("import:locations"))):
    text = (await file.read()).decode()
    rows = csv.DictReader(io.StringIO(text))
    ok, errors = 0, []
    for idx, row in enumerate(rows, start=2):
        try:
            db.add(Location(tenant_id=user.tenant_id, name=row["name"], capacity=float(row.get("capacity") or 0) or None))
            ok += 1
        except Exception as exc:  # noqa: PERF203
            errors.append({"row": idx, "error": str(exc)})
    db.commit()
    return CSVImportResult(success_count=ok, fail_count=len(errors), row_errors=errors)
