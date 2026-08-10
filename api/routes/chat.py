import time

from fastapi import APIRouter, HTTPException
from ollama import AsyncClient
from pydantic import BaseModel, Field

from config import get_settings

settings = get_settings()

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    model: str = Field(default_factory=lambda: get_settings().default_model)


class GenerateResponse(BaseModel):
    response: str
    model: str
    processing_time: float


@router.post("/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest) -> GenerateResponse:
    client = AsyncClient(host=settings.ollama_host)
    start = time.perf_counter()

    try:
        result = await client.chat(
            model=payload.model,
            messages=[{"role": "user", "content": payload.prompt}],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama request failed: {exc}",
        ) from exc

    elapsed = time.perf_counter() - start

    return GenerateResponse(
        response=result["message"]["content"],
        model=payload.model,
        processing_time=round(elapsed, 3),
    )