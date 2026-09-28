import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.core.config import get_settings
from app.services.embeddings import get_embedder
from app.services.llm import get_llm, model_label

logger = logging.getLogger("uvicorn.error")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    start = time.perf_counter()
    get_embedder()
    _, _, device = get_llm()
    logger.info(
        "Models loaded in %.1fs (LLM: %s on %s)",
        time.perf_counter() - start, model_label(), device,
    )
    yield


app = FastAPI(title=settings.app_name, version="0.3.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.include_router(health_router)
app.include_router(chat_router)
