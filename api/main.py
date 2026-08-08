from fastapi import FastAPI

app = FastAPI(
    title="SAGE API",
    description="Self-Hosted AI for Grounded Explanation — native backend service",
    version="0.1.0",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "mode": "native"}