from app.core.config import get_settings
from app.services.embeddings import embed_query
from app.services.vector_store import search

# (question, expected source file, accepted section prefixes)
QUESTIONS = [
    ("What tech stack does Santa use?", "projects/santa.md", ["Tech stack"]),
    ("Which technologies were used to build ColdBrew?", "projects/coldbrew.md", ["Tech stack"]),
    ("What features does the car marketplace have?", "projects/santa.md", ["Key features"]),
    ("How does ordering work in ColdBrew?", "projects/coldbrew.md", ["Key features", "Architecture"]),
    ("How accurate is the food image classifier?", "projects/menu-detector.md", ["Results"]),
    ("How did Juno clean the scraped kebab images?", "projects/menu-detector.md", ["The data problem"]),
    ("How fast is the face detection?", "projects/face-detection.md", ["Results"]),
    ("How does this assistant work?", "projects/juno-assistant.md", ["How it works"]),
    ("Where did Juno study?", "education-experience.md", ["Education"]),
    ("What awards or scholarships has Juno received?", "education-experience.md", ["Awards and scholarships"]),
    ("Was Juno a leader in any organization?", "education-experience.md", ["Leadership"]),
    ("What languages does Juno speak?", "about.md", ["Languages"]),
    ("How can I contact Juno?", "about.md", ["Contact"]),
    ("Does Juno need visa sponsorship?", "about.md", ["Work authorization"]),
    ("What kind of job is Juno looking for?", "about.md", ["What he is looking for"]),
    ("What are Juno's strongest skills?", "skills.md", ["Strongest areas"]),
]


def find_rank(points, source: str, sections: list[str]) -> int | None:
    for rank, point in enumerate(points, start=1):
        p = point.payload
        if p["source"].endswith(source) and any(p["section"].startswith(s) for s in sections):
            return rank
    return None


def main() -> None:
    settings = get_settings()
    print(f"Embedding model: {settings.embedding_model}\n")

    ranks = []
    for question, source, sections in QUESTIONS:
        points = search(settings.qdrant_collection, embed_query(question), limit=5)
        rank = find_rank(points, source, sections)
        ranks.append(rank)
        print(f"{'#' + str(rank) if rank else 'miss':>5}  {question}")

    n = len(QUESTIONS)
    for k in (1, 3, 5):
        hits = sum(1 for r in ranks if r is not None and r <= k)
        print(f"Hit@{k}: {hits}/{n} ({hits / n:.0%})", end="   ")
    print()


if __name__ == "__main__":
    main()
