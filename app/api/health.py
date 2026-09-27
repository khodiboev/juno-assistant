from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.services.vector_store import get_client

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: Settings = Depends(get_settings)):
    try:
        collections = [c.name for c in get_client().get_collections().collections]
        qdrant = {"status": "ok", "collections": collections}
    except Exception as e:
        qdrant = {"status": "error", "detail": str(e)}

    return {"status": "ok", "app": settings.app_name, "qdrant": qdrant}
