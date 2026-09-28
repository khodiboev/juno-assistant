# Project: Juno Assistant — this AI assistant

## Summary
Juno Assistant is the chatbot you are talking to. It answers questions about Juno's background, skills and projects using retrieval-augmented generation (RAG): it searches Juno's own documents for the most relevant passages and a small open-source language model writes the answer from them, citing its sources.
Code: https://github.com/khodiboev/juno-assistant
Live: https://ask.santacar.tech

## How it works
1. Juno's documents (about, skills, experience and one file per project) are split into chunks by their headings.
2. Each chunk is turned into a vector (an embedding) with the BAAI/bge-small-en-v1.5 model and stored in the Qdrant vector database.
3. When a question arrives, it is embedded the same way and Qdrant returns the five most similar chunks.
4. Chunks below a calibrated similarity threshold are dropped. If nothing relevant remains, the assistant says it does not know instead of guessing.
5. A small language model that runs locally writes a short answer using only the remaining chunks.

## How it was evaluated
Juno measured the assistant with his own test sets. Retrieval: switching the embedding model and adding a context header to every chunk raised the share of questions whose correct passage is in the top five results from 81% to 100%. Safety: the similarity threshold was calibrated so that off-topic questions (weather, recipes) are refused. Answers: each answer is checked for required facts and for invented numbers, links or accounts that do not appear in the source passages.

## Tech stack
Backend: Python, FastAPI, Pydantic, Qdrant, sentence-transformers, Hugging Face Transformers, PyTorch, Docker Compose. Frontend: Next.js (App Router), React, TypeScript, with answers streamed word by word.

## Why these choices
Everything runs locally and for free on a normal server, with no paid AI API. The trade-off is that a small language model is much weaker than commercial models, so answers are short and are always grounded in Juno's documents.
