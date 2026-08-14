"""Load ingestion chunks and persist a simple search corpus for 天喜腦."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHUNKS_DIR = ROOT / "ingestion" / "chunks"
INDEX_DIR = ROOT / "brain" / "index"
CORPUS_PATH = INDEX_DIR / "corpus.json"


def _tokenize(text: str) -> list[str]:
    """Lightweight tokenizer: CJK chars as 1-grams + alphanumeric tokens."""
    text = text.lower()
    parts = re.findall(r"[\u4e00-\u9fff]|[a-z0-9_\-]+", text)
    # also keep bigrams of consecutive CJK for slightly better recall
    out: list[str] = []
    for i, p in enumerate(parts):
        out.append(p)
        if (
            i + 1 < len(parts)
            and len(p) == 1
            and "\u4e00" <= p <= "\u9fff"
            and len(parts[i + 1]) == 1
            and "\u4e00" <= parts[i + 1] <= "\u9fff"
        ):
            out.append(p + parts[i + 1])
    return out


def load_all_chunks(chunks_dir: Path | None = None) -> list[dict[str, Any]]:
    """Load every chunk JSON produced by ingestion CLI."""
    d = chunks_dir or CHUNKS_DIR
    if not d.exists():
        return []
    items: list[dict[str, Any]] = []
    seen_hash: set[str] = set()
    for path in sorted(d.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(data, list):
            continue
        for ch in data:
            if not isinstance(ch, dict):
                continue
            content = (ch.get("content") or "").strip()
            if not content:
                continue
            h = ch.get("content_hash") or content[:64]
            if h in seen_hash:
                continue
            seen_hash.add(str(h))
            items.append(
                {
                    "id": f"{path.stem}:{len(items)}",
                    "source_id": ch.get("source_id"),
                    "title": ch.get("title") or path.stem,
                    "content": content,
                    "content_hash": h,
                    "metadata": ch.get("metadata") or {},
                    "race_date": ch.get("race_date"),
                }
            )
    return items


def save_corpus(docs: list[dict[str, Any]], path: Path | None = None) -> Path:
    path = path or CORPUS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "doc_count": len(docs),
        "documents": docs,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_corpus(path: Path | None = None) -> list[dict[str, Any]]:
    path = path or CORPUS_PATH
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("documents") or [])
