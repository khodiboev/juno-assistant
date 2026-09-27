# Juno Assistant

An AI assistant that answers recruiters' questions about my background, skills and projects — built with retrieval-augmented generation (RAG) and a small open-source language model that runs locally, with no paid AI API.

It answers **only** from my own documents, shows the sources of every answer, and declines questions it has no information about.

## How it works

1. **Knowledge base** — Markdown files in `knowledge/` (about, skills, education, one file per project), split into chunks by their headings.
2. **Embeddings** — each chunk gets a context header (person · document · section) and is embedded with `BAAI/bge-small-en-v1.5`, then stored in **Qdrant**.
3. **Retrieval** — the question is embedded with a query instruction; the five most similar chunks are returned.
4. **Guardrail** — chunks below a calibrated similarity threshold (0.58) are dropped; if none remain, the model is not called at all.
5. **Generation** — `Qwen2.5-1.5B-Instruct` answers from the chunks only (system prompt + one example); answers stream to the browser as NDJSON.
6. **Follow-ups** — if a short follow-up ("tell me more") finds nothing on its own, it is searched together with the previous question.

## Evaluation

Every change was measured on small test sets in `scripts/`, and results are saved in `eval_results/`.

**Retrieval** — is the correct passage in the top results? (16 questions)

| Setup | Hit@1 | Hit@5 |
|---|---|---|
| all-MiniLM-L6-v2 (baseline) | 62% | 81% |
| bge-small-en-v1.5 | 62% | 88% |
| bge-small + context header on every chunk | **81%** | **100%** |

**Answers** — required facts present, no invented numbers, links or accounts (11 questions + 2 off-topic)

| Model | Passed | Grounded | Off-topic declined | Avg. latency (Apple M4, MPS) |
|---|---|---|---|---|
| TinyLlama-1.1B-Chat | 5/11 | 6/11 | 2/2 | 1.8 s |
| Qwen2.5-0.5B-Instruct | 9/11 | 11/11 | 2/2 | 0.7 s |
| **Qwen2.5-1.5B-Instruct** | **11/11** | **11/11** | 2/2 | 1.5 s |

The original plan used TinyLlama; the grounding check showed it invented facts in almost half of its answers, so the project switched to Qwen2.5-1.5B.

**Guardrail** — the similarity threshold was calibrated on relevant vs. off-topic questions (`scripts/calibrate_threshold.py`): the lowest relevant score was 0.622 and the highest off-topic score 0.544.

## Tech stack

- **Backend:** Python, FastAPI, Pydantic, Qdrant, sentence-transformers, Hugging Face Transformers, PyTorch
- **Frontend:** Next.js (App Router), React, TypeScript, CSS Modules
- **Infrastructure:** Docker Compose

## Project structureapp/ FastAPI backend
api/ /health, /chat, /chat/stream
services/ chunker, embeddings, vector store, LLM, RAG
schemas/ request and response models
knowledge/ the assistant's knowledge base (Markdown)
scripts/ ingest, search, evaluation and calibration
eval_results/ saved evaluation runs
web/ Next.js chat interface
docker-compose.yml Qdrant

## Run locally

Requirements: Python 3.12, Node.js 20+, Docker.

```bash
# 1. Vector database
docker compose up -d

# 2. Backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m scripts.ingest              # chunk, embed and store the knowledge base
uvicorn app.main:app --reload --reload-dir app   # http://localhost:8000/docs

# 3. Frontend
cd web
cp .env.example .env.local
npm install
npm run dev                           # http://localhost:3100
```

Evaluate:

```bash
python -m scripts.eval_retrieval
python -m scripts.eval_answers
```

## Roadmap

- Deploy with a public link
- LoRA fine-tuning of Qwen2.5-0.5B to reach 1.5B quality at a third of the memory
