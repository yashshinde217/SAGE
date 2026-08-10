import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from services import ingestion, vector_store

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/ingest")
async def ingest_document(file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    suffix = Path(file.filename).suffix
    tmp_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        chunks = ingestion.ingest_file(tmp_path, source_file_name=file.filename)

        if not chunks:
            raise HTTPException(
                status_code=422,
                detail="Document parsed but produced no chunks",
            )

        vector_store.upsert_chunks(
            ids=[c.chunk_id for c in chunks],
            texts=[c.text for c in chunks],
            metadatas=[
                {
                    "source_file": c.source_file,
                    "page_number": c.page_number if c.page_number is not None else -1,
                    "chunk_id": c.chunk_id,
                }
                for c in chunks
            ],
        )

        return {
            "filename": file.filename,
            "total_chunks": len(chunks),
            "status": "indexed",
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()


@router.get("/stats")
def document_stats():
    return vector_store.get_stats()