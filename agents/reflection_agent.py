"""Reflection Agent skeleton — compare predictions vs results and write memory notes.

Lightweight, dependency-optional skeleton.
Produces a structured reflection note for local chunks or optional Mem0.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_reflection_note(
    *,
    race_date: str,
    predictions: list[dict[str, Any]],
    results: list[dict[str, Any]],
    model_version: str | None = None,
) -> dict[str, Any]:
    """Build a structured reflection note from predictions and actual results."""
    pred_names = []
    for p in predictions[:8]:
        name = p.get("name_ch") or p.get("name") or p.get("horse") or str(p)[:40]
        pred_names.append(str(name))

    result_names = []
    for r in results[:8]:
        name = r.get("name_ch") or r.get("name") or r.get("horse") or str(r)[:40]
        result_names.append(str(name))

    hit = len(set(pred_names) & set(result_names))

    summary = (
        f"Race day {race_date}\n"
        f"Model version: {model_version or 'unknown'}\n"
        f"Top predictions: {', '.join(pred_names) or 'n/a'}\n"
        f"Actual (sample): {', '.join(result_names) or 'n/a'}\n"
        f"Name overlap (rough hit signal): {hit}\n"
        f"Reflection: review factor contributions and cold/hot bias for next cycle."
    )

    return {
        "type": "race_reflection",
        "race_date": race_date,
        "model_version": model_version,
        "predicted": pred_names,
        "actual_sample": result_names,
        "overlap": hit,
        "summary": summary,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def reflection_to_mem0_payload(
    note: dict[str, Any], user_id: str = "tianxi-brain"
) -> dict[str, Any]:
    """Shape a note into a Mem0-friendly add() payload (optional)."""
    return {
        "messages": [
            {
                "role": "assistant",
                "content": note.get("summary") or str(note),
            }
        ],
        "user_id": user_id,
        "metadata": {
            "type": "race_reflection",
            "race_date": note.get("race_date"),
            "model_version": note.get("model_version"),
        },
    }
