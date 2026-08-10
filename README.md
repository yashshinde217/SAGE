# SAGE 🧠
**Self-Hosted AI for Grounded Explanation**

[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Native-white?style=for-the-badge&logo=ollama)](https://ollama.com/)
[![Tailwind CSS v4](https://img.shields.io/badge/Tailwind_v4-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)

SAGE is an enterprise-grade, 100% air-gapped Retrieval-Augmented Generation (RAG) platform. It processes local documents into dense mathematical embeddings and uses open-weight local LLMs to generate answers that are strictly grounded in the retrieved context—complete with verifiable, page-level inline citations. 

Zero cloud APIs. Zero data leakage. Total data sovereignty.

---

## 🖥️ The Obsidian Glass Workspace

SAGE is designed with a dark, highly technical UI/UX prioritizing focus and legibility for dense information workspaces. 

> **[ 📸 INSERT: Screenshot of the full Dual-Pane Workspace ]**

* **Glassmorphic Dual-Pane:** A frosted-glass split layout featuring a conversational chat panel on the left and the Knowledge Vault on the right.
* **Interactive Citations:** Source chips rendered as neon-accented glass elements. Clicking a citation instantly reveals the exact Markdown-rendered text chunk in the Knowledge Vault.
* **Telemetry HUD:** A persistent, unobtrusive status badge polling real-time hardware utilization (CPU/RAM) via `psutil`.

> **[ 📸 INSERT: Close-up screenshot of the Telemetry HUD and Source Chips ]**

---

## ⚙️ System Architecture

SAGE operates on a decoupled, natively executed microservices architecture, built for maximum modularity and resilience without the overhead of Docker containerization.

```text
[ Local Documents ] ──( IBM Docling )──> [ Semantic Chunks ]
                                                │
                                                ▼ (Nomic Embeddings)
                                         [ ChromaDB Vector Store ]
                                                │
[ User Query ] ────( Hybrid Search )────────────┤
                                                ▼
[ Glassmorphic UI ] <──( Ollama Native )── [ Grounded Prompt w/ Context ]
```

### The Tech Stack
* **Frontend:** Next.js 16 (App Router), Tailwind CSS v4, Framer Motion, React Markdown.
* **Backend:** Python (FastAPI), `uv` package manager, Pydantic, IBM Docling.
* **AI & Data:** Ollama (qwen2.5 / Llama 3), ChromaDB (Native in-process), Sentence Transformers.

---

## 🔍 Deep Dive: The Hybrid Search Engine

Standard RAG systems rely entirely on semantic vector search, which understands concepts but frequently fails to retrieve exact technical terms, acronyms, or specific ID numbers. SAGE solves this by running a **Dual-Pass Retrieval Engine**.

When a query is submitted, SAGE executes two searches in parallel:
1. **Semantic Search (ChromaDB):** Finds contextual meaning using `nomic-embed-text-v1.5` embeddings.
2. **Keyword Search (BM25):** Executes an exact-match token search across the document corpus.

### Reciprocal Rank Fusion (RRF)
To mathematically merge these two distinct scoring systems, SAGE applies Reciprocal Rank Fusion. The algorithm re-ranks the combined documents by assigning a score based on their position in both lists, using the following formula:

$RRF\_Score = \sum_{r \in R} \frac{1}{k + \text{rank}_r}$

*(Where $k$ is a smoothing constant, typically set to 60, and $\text{rank}$ is the document's position in the respective search result).*

This guarantees that document chunks containing both the conceptual meaning *and* the exact keywords bubble to the absolute top of the context window before being fed to the LLM.

---

## 🚀 Getting Started

SAGE runs entirely natively on your local hardware.

### Prerequisites
1. **Ollama:** Install the native desktop app from [ollama.com](https://ollama.com).
2. **Node.js:** v20+ for the frontend.
3. **Python:** v3.11+ with `uv` installed (`pip install uv`).
4. **Test Model:** Pull a lightweight model for testing:
   ```bash
   ollama pull qwen2.5:0.5b
   ```

### One-Click Launch
We have included native launch scripts to boot both the FastAPI backend and Next.js frontend concurrently. 

**For Linux / macOS:**
```bash
bash start.sh
```

**For Windows:**
```cmd
.\start.bat
```
Navigate to `http://localhost:3000` to enter the workspace.

---

## 🗺️ Roadmap & Future Optimizations
- [ ] **BM25 Caching:** Serialize the BM25 index to disk during ingestion to prevent rebuild-on-query overhead at scale.
- [ ] **Streaming Responses:** Implement SSE (Server-Sent Events) in the FastAPI `/generate` endpoint for real-time token streaming.
- [ ] **Automated Testing:** Implement a comprehensive `pytest` and `vitest` suite for CI/CD integration.