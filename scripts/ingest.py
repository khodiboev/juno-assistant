import time
from pathlib import Path

from app.core.config import get_settings
from app.services.chunker import chunk_directory
from app.services.embeddings import embed_texts
from app.services.vector_store import get_client, recreate_collection, upsert_chunks


def main() -> None:
    settings = get_settings()
    start = time.time()

    chunks = chunk_directory(
        Path(settings.knowledge_dir),
        settings.chunk_size_chars,
        settings.chunk_overlap_chars,
    )
    print(f"Chunks: {len(chunks)}")

    vectors = embed_texts([chunk.for_embedding(settings.knowledge_subject) for chunk in chunks])
    print(f"Vectors: {len(vectors)} x {len(vectors[0])} dimensions")

    recreate_collection(settings.qdrant_collection, dim=len(vectors[0]))
    upsert_chunks(settings.qdrant_collection, chunks, vectors)

    count = get_client().count(settings.qdrant_collection).count
    print(f"Stored in Qdrant collection '{settings.qdrant_collection}': {count} points")
    print(f"Done in {time.time() - start:.1f}s")


if __name__ == "__main__":
    main()
