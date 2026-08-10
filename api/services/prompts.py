SYSTEM_PROMPT = (
    "You are SAGE. Answer strictly based on the provided context. "
    "If the context does not contain the answer, say "
    "'I cannot answer this based on the provided documents.' "
    "When making a claim, cite the source inline using exactly the format "
    "[Source: {source_file}, Page: {page_number}]."
)


def _format_chunk(chunk: dict) -> str:
    source_file = chunk.get("source_file", "unknown")
    page_number = chunk.get("page_number")
    page_display = page_number if page_number not in (None, -1) else "N/A"
    text = chunk.get("text", "")
    return f"[Source: {source_file}, Page: {page_display}]\n{text}"


def build_rag_prompt(query: str, context_chunks: list[dict]) -> list[dict]:
    context_block = "\n\n".join(_format_chunk(c) for c in context_chunks)

    user_content = (
        f"Context:\n{context_block}\n\nQuestion: {query}"
        if context_chunks
        else f"Context: (no relevant documents found)\n\nQuestion: {query}"
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]