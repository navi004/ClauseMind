"""
loader.py — Extract text from any insurance PDF, page by page
"""

import PyPDF2


def load_pdf(filepath: str) -> str:
    """Returns full text (used for chunking)."""
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        pages  = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages)
    print(f"[loader] PDF loaded: {filepath}")
    print(f"[loader] Pages: {len(reader.pages)} | Words: {len(text.split()):,}")
    return text


def load_pdf_by_page(filepath: str) -> list[str]:
    """Returns list of text per page (used for page-aware chunking)."""
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        return [page.extract_text() or "" for page in reader.pages]