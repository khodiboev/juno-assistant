import sys

from app.core.config import get_settings
from app.services.embeddings import embed_query
from app.services.vector_store import search

question = " ".join(sys.argv[1:]) or "What tech stack does Santa use?"
settings = get_settings()

results = search(settings.qdrant_collection, embed_query(question), limit=5)

print(f"Question: {question}\n")
for point in results:
    p = point.payload
    print(f"{point.score:.3f}  {p['source']}  |  {p['section']}")
