import json
import re
import time
from pathlib import Path

from app.core.config import get_settings
from app.services.embeddings import get_embedder
from app.services.llm import get_llm
from app.services.rag import answer_question

# (question, required facts) — each fact is a list of accepted spellings
CASES = [
    ("What tech stack does Santa use?", [["nestjs"], ["graphql"], ["next.js", "nextjs"]]),
    ("Which technologies were used to build ColdBrew?", [["express"], ["react"], ["mongodb"]]),
    ("Where did Juno study?", [["smit", "seoul media"], ["namangan"]]),
    ("What awards or scholarships has Juno received?", [["scholarship"], ["academic excellence"]]),
    ("What languages does Juno speak?", [["english"], ["uzbek"], ["korean"]]),
    ("How can I contact Juno?", [["fikrchi@gmail.com"]]),
    ("Does Juno need visa sponsorship?", [["e-7"]]),
    ("How accurate is the food image classifier?", [["93.7", "94.8"]]),
    ("What kind of job is Juno looking for?", [["full-stack", "full stack"], ["korea"]]),
    ("How does this assistant work?", [["qdrant", "vector", "retriev"]]),
    ("Was Juno a leader in any organization?", [["president"], ["uzbek"]]),
]

OFF_TOPIC = [
    "What is the weather in Seoul today?",
    "How do I cook plov?",
]

FORBIDDEN = ["the context", "given context", "provided context", "facts:", "the notes", "not mentioned", "[1]"]

NUMBER = re.compile(r"\b\d+(?:[.,]\d+)?\b")
HANDLE = re.compile(r"@\w+")
URL = re.compile(r"https?://\S+|www\.\S+|\b[\w-]+\.(?:com|net|org|io|tech|dev)\b")
SOCIAL = ["twitter", "instagram", "facebook", "tiktok", "youtube", "telegram"]


def check_facts(answer: str, facts: list[list[str]]) -> tuple[int, list[str]]:
    low = answer.lower()
    found = sum(1 for options in facts if any(option in low for option in options))
    bad = [phrase for phrase in FORBIDDEN if phrase in low]
    return found, bad


def unsupported(answer: str, context: str) -> list[str]:
    low_answer, low_context = answer.lower(), context.lower()
    items = set(NUMBER.findall(low_answer)) | set(HANDLE.findall(low_answer))
    items |= {u.rstrip(".,)") for u in URL.findall(low_answer)}
    items |= {s for s in SOCIAL if s in low_answer}
    return sorted(item for item in items if item not in low_context)


def main() -> None:
    settings = get_settings()
    print(f"LLM: {settings.llm_model}")

    start = time.time()
    get_embedder()
    _, _, device = get_llm()
    print(f"Models loaded in {time.time() - start:.1f}s (device: {device})\n")

    records = []
    passed = facts_found = facts_total = grounded = 0
    latencies = []

    for question, facts in CASES:
        start = time.time()
        result = answer_question(question)
        latency = time.time() - start
        latencies.append(latency)

        found, bad = check_facts(result.answer, facts)
        invented = unsupported(result.answer, result.context)
        ok = found == len(facts) and not bad and not invented
        passed += ok
        grounded += not invented
        facts_found += found
        facts_total += len(facts)

        print(f"{'PASS' if ok else 'FAIL'}  facts {found}/{len(facts)}  {latency:4.1f}s  {question}")
        if bad:
            print(f"      forbidden: {bad}")
        if invented:
            print(f"      invented:  {invented}")
        print(f"      -> {result.answer[:220]}")
        records.append({"question": question, "answer": result.answer, "pass": ok,
                        "facts_found": found, "facts_total": len(facts), "forbidden": bad,
                        "invented": invented, "latency_s": round(latency, 2)})

    refused = 0
    for question in OFF_TOPIC:
        result = answer_question(question)
        ok = not result.used_context
        refused += ok
        print(f"{'PASS' if ok else 'FAIL'}  off-topic  {question}")
        records.append({"question": question, "answer": result.answer, "pass": ok, "off_topic": True})

    n = len(CASES)
    avg_latency = sum(latencies) / len(latencies)
    print(f"\nAnswers passed:    {passed}/{n} ({passed / n:.0%})")
    print(f"Fact coverage:     {facts_found}/{facts_total} ({facts_found / facts_total:.0%})")
    print(f"Grounded answers:  {grounded}/{n} ({grounded / n:.0%})")
    print(f"Off-topic refused: {refused}/{len(OFF_TOPIC)}")
    print(f"Avg latency:       {avg_latency:.1f}s")

    out_dir = Path("eval_results")
    out_dir.mkdir(exist_ok=True)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", settings.llm_model).strip("-").lower()
    out_file = out_dir / f"answers_{slug}.json"
    out_file.write_text(json.dumps({
        "llm_model": settings.llm_model,
        "summary": {
            "passed": passed, "total": n,
            "fact_coverage": round(facts_found / facts_total, 3),
            "grounded": grounded,
            "off_topic_refused": refused,
            "avg_latency_s": round(avg_latency, 2),
        },
        "results": records,
    }, indent=2, ensure_ascii=False))
    print(f"Saved: {out_file}")


if __name__ == "__main__":
    main()
