import json
import time

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest, ChatResponse, SourceOut
from app.services.rag import answer_question, stream_answer

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


@router.post("/chat/stream")
def chat_stream(body: ChatRequest) -> StreamingResponse:
    def events():
        start = time.perf_counter()
        try:
            for event in stream_answer(body.question):
                yield json.dumps(event) + "\n"
        except Exception:
            yield json.dumps({"type": "error", "message": "The assistant failed to answer. Please try again."}) + "\n"
        yield json.dumps({"type": "done", "latency_ms": int((time.perf_counter() - start) * 1000)}) + "\n"

    return StreamingResponse(
        events(),
        media_type="application/x-ndjson",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
