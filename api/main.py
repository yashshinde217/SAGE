from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routes import chat, documents, system

settings = get_settings()

app = FastAPI(
    title="SAGE API",
    description="Self-Hosted AI for Grounded Explanation — native backend service",
    version="0.6.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(system.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "native"}