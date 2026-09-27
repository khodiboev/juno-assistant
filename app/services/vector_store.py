from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import get_settings
from app.services.chunker import Chunk


@lru_cache
def get_client() -> QdrantClient:
    settings = get_settings()
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
        timeout=10,
    )


def recreate_collection(name: str, dim: int) -> None:
    client = get_client()
    if client.collection_exists(name):
        client.delete_collection(name)
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )


def upsert_chunks(name: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
    points = [
        PointStruct(
            id=i,
            vector=vector,
            payload={
                "source": chunk.source,
                "title": chunk.title,
                "section": chunk.section,
                "text": chunk.text,
            },
        )
        for i, (chunk, vector) in enumerate(zip(chunks, vectors))
    ]
    get_client().upsert(collection_name=name, points=points, wait=True)


def search(name: str, vector: list[float], limit: int = 5):
    result = get_client().query_points(
        collection_name=name,
        query=vector,
        limit=limit,
        with_payload=True,
    )
    return result.points
