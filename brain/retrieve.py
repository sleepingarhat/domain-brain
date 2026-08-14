"""BM25 retrieval for 天喜腦 — pure Python, no embedding API, no Dify credits."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from brain.store import _tokenize, load_all_chunks, load_corpus, save_corpus


@dataclass
class Hit:
    score: float
    title: str
    content: str
    source_id: str | None
    metadata: dict[str, Any]
    doc_id: str


class BM25:
    """Minimal BM25Okapi."""

    def __init__(self, corpus_tokens: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_tokens = corpus_tokens
        self.n = len(corpus_tokens)
        self.doc_len = [len(doc) for doc in corpus_tokens]
        self.avgdl = sum(self.doc_len) / self.n if self.n else 0.0
        self.df: dict[str, int] = {}
        for doc in corpus_tokens:
            for t in set(doc):
                self.df[t] = self.df.get(t, 0) + 1
        self.idf = {
            t: math.log(1 + (self.n - df + 0.5) / (df + 0.5))
            for t, df in self.df.items()
        }

    def score(self, query_tokens: list[str]) -> list[float]:
        scores = [0.0] * self.n
        if self.n == 0 or self.avgdl == 0:
            return scores
        for t in query_tokens:
            if t not in self.idf:
                continue
            idf = self.idf[t]
            for i, doc in enumerate(self.corpus_tokens):
                freq = doc.count(t)
                if freq == 0:
                    continue
                denom = freq + self.k1 * (1 - self.b + self.b * self.doc_len[i] / self.avgdl)
                scores[i] += idf * (freq * (self.k1 + 1)) / denom
        return scores


def build_index() -> dict[str, Any]:
    """Rebuild corpus from all ingestion chunk files."""
    docs = load_all_chunks()
    path = save_corpus(docs)
    return {"doc_count": len(docs), "path": str(path)}


def search(query: str, top_k: int = 5) -> list[Hit]:
    docs = load_corpus()
    if not docs:
        # auto-build once if empty
        build_index()
        docs = load_corpus()
    if not docs:
        return []

    tokens_list = [_tokenize((d.get("title") or "") + "\n" + (d.get("content") or "")) for d in docs]
    bm25 = BM25(tokens_list)
    q_tokens = _tokenize(query)
    scores = bm25.score(q_tokens)
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

    hits: list[Hit] = []
    for i in ranked[:top_k]:
        if scores[i] <= 0:
            continue
        d = docs[i]
        hits.append(
            Hit(
                score=round(scores[i], 4),
                title=str(d.get("title") or ""),
                content=str(d.get("content") or ""),
                source_id=d.get("source_id"),
                metadata=d.get("metadata") or {},
                doc_id=str(d.get("id") or i),
            )
        )
    return hits
