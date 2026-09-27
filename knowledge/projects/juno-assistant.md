# Project: Juno Assistant — this AI assistant

## Summary
Juno Assistant is the chatbot you are talking to. It answers questions about Juno's background, skills and projects using retrieval-augmented generation (RAG): it searches Juno's own documents for the most relevant passages and a language model writes the answer from them, citing its sources.
Code: https://github.com/khodiboev/juno-assistant

## How it works
1. Juno's documents (about, skills, experience and one file per project) are split into small chunks.
2. Each chunk is turned into a vector (an embedding) with the all-MiniLM-L6-v2 sentence-transformers model and stored in the Qdrant vector database.
3. When a question arrives, it is embedded the same way and Qdrant returns the most similar chunks.
4. TinyLlama, a small 1.1-billion-parameter open-source language model, writes an answer using only those chunks.
5. If no chunk is relevant enough, the assistant says it does not know instead of guessing.

## Tech stack
Python, FastAPI, Pydantic, Qdrant, sentence-transformers, Hugging Face Transformers, TinyLlama, Docker Compose. A Next.js chat interface and LoRA fine-tuning of TinyLlama are planned.

## Why these choices
Everything runs locally and for free on a normal server, with no paid AI API. The trade-off is that TinyLlama is much smaller than commercial models, so answers are short and can take several seconds.
