from fastapi import APIRouter, Depends
from qdrant_client import QdrantClient

from app.core.config import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: Settings = Depends(get_settings)):
    try:
        client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key, timeout=3)
        collections = [c.name for c in client.get_collections().collections]
        qdrant = {"status": "ok", "collections": collections}
    except Exception as e:
        qdrant = {"status": "error", "detail": str(e)}

    return {"status": "ok", "app": settings.app_name, "qdrant": qdrant}
