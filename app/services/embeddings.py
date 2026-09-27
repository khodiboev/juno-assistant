from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.core.config import get_settings


@lru_cache
def get_embedder() -> SentenceTransformer:
    return SentenceTransformer(get_settings().embedding_model, device="cpu")


def embed_texts(texts: list[str]) -> list[list[float]]:
    vectors = get_embedder().encode(
        texts,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vectors.tolist()


def embed_query(question: str) -> list[float]:
    prefix = get_settings().embedding_query_prefix
    return embed_texts([prefix + question])[0]
