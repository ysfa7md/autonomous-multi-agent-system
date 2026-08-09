"""
agent/rag.py
Lightweight retrieval over uploaded documents. Deliberately dependency
-light (keyword overlap, no embeddings) so the assignment runs with
zero extra services. Swap `retrieve()` for a FAISS/Chroma-backed
version later without touching the graph — the function signature is
the seam.
"""
import re
from io import BytesIO

from pypdf import PdfReader


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping word-based chunks."""
    words = text.split()
    if not words:
        return []
    step = max(chunk_size - overlap, 1)
    chunks = []
    for i in range(0, len(words), step):
        chunk = " ".join(words[i : i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def load_pdf(file_bytes: bytes) -> list[str]:
    """Extract and chunk text from an uploaded PDF's raw bytes."""
    reader = PdfReader(BytesIO(file_bytes))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return chunk_text(text)


def _score(query: str, chunk: str) -> int:
    """Naive keyword-overlap score — enough to demo grounded retrieval."""
    q_words = set(re.findall(r"\w+", query.lower()))
    c_words = set(re.findall(r"\w+", chunk.lower()))
    return len(q_words & c_words)


def retrieve(query: str, chunks: list[str], k: int = 3) -> list[str]:
    """Return the top-k chunks most relevant to the query."""
    if not chunks:
        return []
    scored = sorted(chunks, key=lambda c: _score(query, c), reverse=True)
    top = [c for c in scored[:k] if _score(query, c) > 0]
    return top or scored[:k]
