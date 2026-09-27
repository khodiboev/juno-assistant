import time

from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse, SourceOut
from app.services.rag import answer_question

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    start = time.perf_counter()
    result = answer_question(body.question)
    return ChatResponse(
        answer=result.answer,
        sources=[SourceOut(source=s.source, section=s.section, score=s.score) for s in result.sources],
        used_context=result.used_context,
        latency_ms=int((time.perf_counter() - start) * 1000),
    )
