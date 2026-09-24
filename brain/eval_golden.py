"""Golden-query gate for 天喜腦 retrieve."""

from __future__ import annotations

import json
from pathlib import Path

from brain.retrieve import search
from brain.store import load_corpus

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "eval" / "golden.json"


def run(path: Path | None = None) -> dict:
    cases = json.loads((path or GOLDEN).read_text(encoding="utf-8"))
    corpus = load_corpus()
    if not corpus:
        return {"skipped": True, "reason": "empty corpus — 先 ingest + compile + build"}

    results = []
    failed = 0
    for case in cases:
        hits = search(case["q"], top_k=8)
        blob = "\n".join(f"{h.title}\n{h.content}" for h in hits)
        ok = any(tok in blob for tok in case["must_any"])
        if not ok:
            failed += 1
        results.append(
            {
                "id": case["id"],
                "q": case["q"],
                "ok": ok,
                "hits": len(hits),
                "top": [h.title for h in hits[:3]],
            }
        )
    return {
        "skipped": False,
        "total": len(cases),
        "failed": failed,
        "passed": len(cases) - failed,
        "results": results,
    }
