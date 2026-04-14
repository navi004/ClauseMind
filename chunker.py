"""
chunker.py — Page-aware chunker, stores page number in every chunk
"""

from config import CHUNK_SIZE, OVERLAP


def chunk_document(text: str, chunk_size: int = CHUNK_SIZE,
                   overlap: int = OVERLAP) -> list[dict]:
    """Standard chunker — used when page info not needed."""
    words, chunks, start = text.split(), [], 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append({
            "chunk_id"  : len(chunks),
            "text"      : " ".join(words[start:end]),
            "word_start": start,
            "word_end"  : end,
            "page"      : None,
        })
        if end == len(words): break
        start += chunk_size - overlap
    print(f"[chunker] {len(chunks)} chunks")
    return chunks


def chunk_by_page(pages: list[str], chunk_size: int = CHUNK_SIZE,
                  overlap: int = OVERLAP) -> list[dict]:
    """
    Page-aware chunker.
    Each chunk knows exactly which page(s) it came from.
    """
    chunks = []

    for page_num, page_text in enumerate(pages, start=1):
        words = page_text.split()
        if not words:
            continue
        start = 0
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunks.append({
                "chunk_id"  : len(chunks),
                "text"      : " ".join(words[start:end]),
                "word_start": start,
                "word_end"  : end,
                "page"      : page_num,       # ← exact page number
            })
            if end == len(words): break
            start += chunk_size - overlap

    print(f"[chunker] {len(chunks)} page-aware chunks")
    return chunks