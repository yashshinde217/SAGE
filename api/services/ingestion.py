import re
from dataclasses import dataclass
from pathlib import Path

from docling.chunking import HybridChunker
from docling.document_converter import DocumentConverter

_converter = DocumentConverter()
_chunker = HybridChunker()

_PLAIN_TEXT_SUFFIXES = {'.md', '.txt'}
_CHUNK_SIZE = 1000
_CHUNK_OVERLAP = 100


@dataclass
class IngestedChunk:
    text: str
    chunk_id: str
    page_number: int | None
    source_file: str


def _chunk_plain_text(text: str, source_file_name: str) -> list[IngestedChunk]:
    """Split plain text into overlapping chunks by paragraph boundaries."""
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
    chunks: list[IngestedChunk] = []
    current, i = [], 0
    length = 0

    for para in paragraphs:
        if length + len(para) > _CHUNK_SIZE and current:
            chunks.append(IngestedChunk(
                text='\n\n'.join(current),
                chunk_id=f"{source_file_name}::chunk_{i}",
                page_number=None,
                source_file=source_file_name,
            ))
            i += 1
            # keep last paragraph for overlap
            current = current[-1:]
            length = len(current[0]) if current else 0
        current.append(para)
        length += len(para)

    if current:
        chunks.append(IngestedChunk(
            text='\n\n'.join(current),
            chunk_id=f"{source_file_name}::chunk_{i}",
            page_number=None,
            source_file=source_file_name,
        ))

    return chunks


def ingest_file(file_path: Path, source_file_name: str) -> list[IngestedChunk]:
    """Convert a document to structured form and split into chunks."""
    if file_path.suffix.lower() in _PLAIN_TEXT_SUFFIXES:
        raw = file_path.read_bytes()
        for enc in ('utf-8-sig', 'utf-16', 'latin-1'):
            try:
                text = raw.decode(enc)
                break
            except (UnicodeDecodeError, ValueError):
                continue
        else:
            text = raw.decode('latin-1')
        return _chunk_plain_text(text, source_file_name)

    result = _converter.convert(str(file_path))
    doc = result.document

    ingested: list[IngestedChunk] = []
    for i, chunk in enumerate(list(_chunker.chunk(dl_doc=doc))):
        page_number = None
        prov = getattr(chunk.meta, "doc_items", None)
        if prov:
            for item in prov:
                if getattr(item, "prov", None):
                    page_number = item.prov[0].page_no
                    break

        ingested.append(IngestedChunk(
            text=chunk.text,
            chunk_id=f"{source_file_name}::chunk_{i}",
            page_number=page_number,
            source_file=source_file_name,
        ))

    return ingested