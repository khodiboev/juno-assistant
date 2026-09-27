import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.core.config import get_settings
from app.services.embeddings import get_embedder
from app.services.llm import get_llm

logger = logging.getLogger("uvicorn.error")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    start = time.perf_counter()
    get_embedder()
    _, _, device = get_llm()
    logger.info(
        "Models loaded in %.1fs (LLM: %s on %s)",
        time.perf_counter() - start, settings.llm_model, device,
    )
    yield


app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan)
app.include_router(health_router)
app.include_router(chat_router)
