from fastapi import APIRouter, Depends

from app.deps import require_permission
from app.schemas import GeneratorMapRequest

router = APIRouter(prefix="/generator", tags=["generator"])


@router.post("/map-schema")
def map_schema(payload: GeneratorMapRequest, user=Depends(require_permission("generator:map"))):
    mapping = []
    for h in payload.headers:
        target = "AssetType.name" if "asset" in h.lower() else "Location.name" if "loc" in h.lower() else "UNKNOWN"
        mapping.append({"source": h, "target": target, "confidence": 0.9 if target != "UNKNOWN" else 0.3})
    return {"mapping": mapping, "domainPack": {"labels": {"ASSET": "Equipment"}, "assetTypes": [], "policies": [], "workflowOverrides": {}, "metadataSchemas": {}}}


@router.post("/apply-domain-pack")
def apply_domain_pack(pack: dict, user=Depends(require_permission("generator:apply"))):
    return {"status": "applied", "labels": len(pack.get("labels", {})), "assetTypes": len(pack.get("assetTypes", []))}
