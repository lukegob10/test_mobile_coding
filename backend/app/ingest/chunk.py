def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    if not text:
        return []
    chunks: list[str] = []
    i = 0
    while i < len(text):
        chunks.append(text[i : i + chunk_size])
        if i + chunk_size >= len(text):
            break
        i += max(chunk_size - overlap, 1)
    return chunks
