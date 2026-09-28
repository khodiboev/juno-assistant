import re
from dataclasses import dataclass, field
from typing import Iterator

from app.core.config import get_settings
from app.services.embeddings import embed_query
from app.services.llm import generate, stream_generate
from app.services.vector_store import search

SYSTEM_PROMPT = (
    "You are Juno Assistant. You answer recruiters' questions about Juno "
    "(Jurabek Khodiboev), a full-stack developer. "
    "Answer only with facts from the notes below. If the notes do not contain the answer, "
    "reply exactly: \"I don't have that information about Juno.\" "
    "Never copy the notes as a list, never mention the notes, and never invent facts. "
    "Write 1 to 3 short sentences in plain English and refer to Juno in the third person."
)

EXAMPLE_QUESTION = "What does Juno do?"
EXAMPLE_ANSWER = (
    "Juno is a full-stack developer based in Seoul who builds web applications end to end, "
    "and he has recently added machine learning and AI to his toolkit."
)

NO_ANSWER = (
    "I don't have information about that. I can answer questions about Juno's "
    "background, skills, education and projects."
)


@dataclass
class Source:
    source: str
    section: str
    score: float


@dataclass
class Answer:
    answer: str
    sources: list[Source] = field(default_factory=list)
    used_context: bool = False
    context: str = ""


def retrieve(question: str):
    settings = get_settings()
    points = search(settings.qdrant_collection, embed_query(question), limit=settings.top_k)
    return [p for p in points if p.score >= settings.min_score]


def build_notes(points) -> str:
    return "\n\n".join(
        f"{p.payload['title']} ({p.payload['section']}): {p.payload['text']}" for p in points
    )


def trim_to_last_sentence(text: str) -> str:
    text = text.strip()
    if not text or text[-1] in ".!?":
        return text
    match = re.search(r"^(.*[.!?])", text, flags=re.DOTALL)
    return match.group(1) if match else text


def build_messages(question: str, notes: str) -> list[dict]:
    return [
        {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nNotes about Juno:\n{notes}"},
        {"role": "user", "content": EXAMPLE_QUESTION},
        {"role": "assistant", "content": EXAMPLE_ANSWER},
        {"role": "user", "content": question},
    ]


def top_sources(points) -> list[Source]:
    settings = get_settings()
    sources: list[Source] = []
    seen = set()
    for point in points:
        key = (point.payload["source"], point.payload["section"])
        if key in seen:
            continue
        seen.add(key)
        sources.append(Source(source=key[0], section=key[1], score=round(point.score, 3)))
        if len(sources) == settings.max_sources:
            break
    return sources


# Words that point back to the previous question ("tell me more about that project")
FOLLOW_UP_HINT = re.compile(
    r"\b(that|it|its|those|them|more|details?|elaborate|else)\b|\bthis (project|one)\b",
    re.IGNORECASE,
)


def is_follow_up(question: str) -> bool:
    return bool(FOLLOW_UP_HINT.search(question)) or len(question.split()) <= 3


def resolve(question: str, previous_question: str | None = None):
    """Decide what to search for. A follow-up ("in detail", "tell me more about that")
    is searched together with the previous question; anything else on its own."""
    follow_up_prompt = f"Earlier question: {previous_question}\nFollow-up: {question}"

    if previous_question and is_follow_up(question):
        points = retrieve(f"{previous_question} {question}")
        if points:
            return follow_up_prompt, points

    points = retrieve(question)
    if points or not previous_question:
        return question, points

    points = retrieve(f"{previous_question} {question}")
    return follow_up_prompt, points


def answer_question(question: str, previous_question: str | None = None) -> Answer:
    prompt_question, points = resolve(question, previous_question)
    if not points:
        return Answer(answer=NO_ANSWER)

    notes = build_notes(points)
    text = trim_to_last_sentence(generate(build_messages(prompt_question, notes)))
    return Answer(answer=text, sources=top_sources(points), used_context=True, context=notes)


def stream_answer(question: str, previous_question: str | None = None) -> Iterator[dict]:
    prompt_question, points = resolve(question, previous_question)
    if not points:
        yield {"type": "sources", "sources": [], "used_context": False}
        yield {"type": "token", "text": NO_ANSWER}
        return

    sources = [vars(s) for s in top_sources(points)]
    yield {"type": "sources", "sources": sources, "used_context": True}

    notes = build_notes(points)
    for piece in stream_generate(build_messages(prompt_question, notes)):
        yield {"type": "token", "text": piece}
