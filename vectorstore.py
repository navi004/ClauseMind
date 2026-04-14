"""
vectorstore.py — Local sentence-transformer embeddings + FAISS index
No API key needed. Runs entirely on your machine.
"""

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
import os
import  pickle

from config import EMBED_MODEL, TOP_K


class VectorStore:
    """
    Builds a FAISS cosine-similarity index over document chunks.
    Embedding runs locally — free, no rate limits.
    """

    def __init__(self, model_name: str = EMBED_MODEL):
        print(f"[vectorstore] Loading embedding model: {model_name} ...")
        self.model  = SentenceTransformer(model_name)
        self.index  = None
        self.chunks = []
        print(f"[vectorstore] Model ready (local)")

    def build(self, chunks: list[dict]) -> None:
        """Embed all chunks and build FAISS index."""
        self.chunks = chunks
        texts = [c["text"] for c in chunks]

        print(f"[vectorstore] Embedding {len(texts)} chunks ...")
        emb = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        emb = emb / np.linalg.norm(emb, axis=1, keepdims=True)   # normalise for cosine

        self.index = faiss.IndexFlatIP(emb.shape[1])
        self.index.add(emb.astype("float32"))

        print(f"[vectorstore] FAISS index: {self.index.ntotal} vectors, dim={emb.shape[1]}")

    def retrieve(self, query: str, top_k: int = TOP_K) -> list[dict]:
        """Return top-k most similar chunks for a query."""
        q = self.model.encode([query], convert_to_numpy=True)
        q = q / np.linalg.norm(q, axis=1, keepdims=True)

        scores, idxs = self.index.search(q.astype("float32"), top_k)
        return [
            {**self.chunks[i], "score": float(s)}
            for s, i in zip(scores[0], idxs[0])
            if i != -1
        ]

    def save(self, path: str) -> None:
        """Save FAISS index and chunks to disk."""
        faiss.write_index(self.index, path + ".index")
        with open(path + ".chunks", "wb") as f:
            pickle.dump(self.chunks, f)
        print(f"[vectorstore] Saved → {path}.index / {path}.chunks")

    def load(self, path: str) -> bool:
        """Load from disk if exists. Returns True if loaded."""
        if os.path.exists(path + ".index") and os.path.exists(path + ".chunks"):
            self.index = faiss.read_index(path + ".index")
            with open(path + ".chunks", "rb") as f:
                self.chunks = pickle.load(f)
            print(f"[vectorstore] Loaded from cache → {path}")
            return True
        return False