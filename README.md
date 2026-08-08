# SAGE — Self-Hosted AI for Grounded Explanation

SAGE is a modular, enterprise-grade, **air-gapped** Retrieval-Augmented
Generation (RAG) system. All services run **natively** on the host —
no Docker, no containers — to keep the stack transparent, debuggable,
and dependency-minimal for air-gapped deployment targets.

## Architecture (Phase 1 baseline)

| Service | Path   | Stack                          | Purpose                          |
|---------|--------|---------------------------------|-----------------------------------|
| API     | `/api` | Python 3.12, FastAPI, `uv`      | Backend, RAG orchestration        |
| Web     | `/web` | Next.js 15 (App Router), TS, Tailwind | Frontend UI                 |
| Data    | `/data`| ChromaDB (local persistent dir) | Vector store persistence          |

## Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) for Python env/dependency management
- Node.js 20+ / npm

## Getting Started

### API

\`\`\`bash
cd api
uv sync
uv run uvicorn main:app --reload --port 8000
\`\`\`

Health check: `GET http://localhost:8000/health`

### Web

\`\`\`bash
cd web
npm install
npm run dev
\`\`\`

App: `http://localhost:3000`

## Data Persistence

ChromaDB vector data is persisted natively to `data/chroma/`. This
directory is git-ignored except for a `.keep` placeholder.

## Project Status

**Phase 1 — Native Scaffolding, Version Control & Local Environment**: complete.
See subsequent phases for RAG pipeline, embedding service, and LLM integration.