from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Juno Assistant"
    cors_origins: list[str] = ["http://localhost:3000"]

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "portfolio"

    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_query_prefix: str = "Represent this sentence for searching relevant passages: "

    knowledge_dir: str = "knowledge"
    knowledge_subject: str = "Juno (Jurabek Khodiboev)"
    chunk_size_chars: int = 1200
    chunk_overlap_chars: int = 200

    llm_model: str = "Qwen/Qwen2.5-1.5B-Instruct"
    llm_device: str = "auto"
    llm_max_new_tokens: int = 200
    llm_temperature: float = 0.0

    top_k: int = 5
    min_score: float = 0.58
    max_sources: int = 3


@lru_cache
def get_settings() -> Settings:
    return Settings()
