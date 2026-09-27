from app.core.config import get_settings
from app.services.embeddings import embed_query
from app.services.vector_store import search
from scripts.eval_retrieval import QUESTIONS

OFF_TOPIC = [
    "What is the weather in Seoul today?",
    "Who won the last World Cup?",
    "Write a Python function that sorts a list.",
    "What is the capital of France?",
    "Tell me a joke.",
    "What is the price of Bitcoin?",
    "How do I cook plov?",
    "Recommend a good movie to watch tonight.",
    "What time is it in New York?",
    "How do I renew my passport?",
]


def top_score(question: str) -> float:
    settings = get_settings()
    points = search(settings.qdrant_collection, embed_query(question), limit=1)
    return points[0].score if points else 0.0


def main() -> None:
    relevant = sorted((top_score(q), q) for q, _, _ in QUESTIONS)
    off_topic = sorted(((top_score(q), q) for q in OFF_TOPIC), reverse=True)

    print("Relevant questions (lowest top score first):")
    for score, q in relevant[:5]:
        print(f"  {score:.3f}  {q}")

    print("\nOff-topic questions (highest top score first):")
    for score, q in off_topic[:5]:
        print(f"  {score:.3f}  {q}")

    lowest_relevant = relevant[0][0]
    highest_off_topic = off_topic[0][0]
    print(f"\nLowest relevant:   {lowest_relevant:.3f}")
    print(f"Highest off-topic: {highest_off_topic:.3f}")
    if lowest_relevant > highest_off_topic:
        print(f"Clean gap -> suggested min_score: {(lowest_relevant + highest_off_topic) / 2:.3f}")
    else:
        print("Groups overlap -> a score threshold alone cannot separate them")


if __name__ == "__main__":
    main()
