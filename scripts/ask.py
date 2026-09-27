import sys
import time

from app.core.config import get_settings
from app.services.embeddings import embed_query, get_embedder
from app.services.llm import get_llm
from app.services.rag import answer_question
from app.services.vector_store import search

questions = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else [
    "What tech stack does Santa use?",
    "Where did Juno study and what awards did he get?",
    "What is the weather in Seoul today?",
]
settings = get_settings()

start = time.time()
get_embedder()
_, _, device = get_llm()
print(f"Models loaded in {time.time() - start:.1f}s (LLM device: {device})\n")

for question in questions:
    print("=" * 70)
    print(f"Question: {question}\n")
    print("Retrieved (score | source | section):")
    for p in search(settings.qdrant_collection, embed_query(question), limit=settings.top_k):
        mark = " " if p.score >= settings.min_score else "x"
        print(f"  {mark} {p.score:.3f} | {p.payload['source']} | {p.payload['section']}")

    start = time.time()
    result = answer_question(question)
    print(f"\nAnswer ({time.time() - start:.1f}s):\n{result.answer}\n")
    print("Sources:", [f"{s.source} | {s.section}" for s in result.sources])
