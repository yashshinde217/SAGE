import time

from fastapi import APIRouter, HTTPException
from ollama import AsyncClient
from pydantic import BaseModel, Field

from config import get_settings
from services.prompts import build_rag_prompt
from services.retrieval import HybridRetriever

settings = get_settings()

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

_retriever = HybridRetriever()


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    model: str = Field(default_factory=lambda: get_settings().default_model)
    top_k: int = Field(default=5, ge=1, le=20)


class SourceMeta(BaseModel):
    source_file: str | None
    page_number: int | None
    chunk_id: str
    text: str


class GenerateResponse(BaseModel):
    response: str
    model: str
    processing_time: float
    sources: list[SourceMeta]


@router.post("/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest) -> GenerateResponse:
    start = time.perf_counter()

    try:
        chunks = _retriever.search(payload.prompt, top_k=payload.top_k)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {exc}",
        ) from exc

    messages = build_rag_prompt(payload.prompt, chunks)

    client = AsyncClient(host=settings.ollama_host)
    try:
        result = await client.chat(model=payload.model, messages=messages)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama request failed: {exc}",
        ) from exc

    elapsed = time.perf_counter() - start

    sources = [
        SourceMeta(
            source_file=c.get("source_file"),
            page_number=c.get("page_number"),
            chunk_id=c["chunk_id"],
            text=c.get("text", ""),
        )
        for c in chunks
    ]

    return GenerateResponse(
        response=result["message"]["content"],
        model=payload.model,
        processing_time=round(elapsed, 3),
        sources=sources,
    )