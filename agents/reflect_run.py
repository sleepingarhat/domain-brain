"""Pair completed results with optional prediction observations.

Green light: tianxi-database has at least one per-race result chunk
for that date, and the date is not in the future (HK).
No results → write nothing. Do not backfill a season.
Predictions are optional observations, never a substitute for results.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from typing import Any

from agents.reflection_agent import build_reflection_note, write_reflection_to_wiki
from brain.extract import DATE_RE, extract_mentions
from brain.store import load_all_chunks
from brain.wiki import today_hk

RESULT_SOURCES = {"tianxi-database"}
PRED_SOURCES = {"tianxi-api"}


def _chunk_date(ch: dict[str, Any]) -> str | None:
    d = ch.get("race_date")
    if d:
        return str(d)[:10]
    meta = ch.get("metadata") or {}
    for key in ("date", "race_date"):
        if meta.get(key):
            return str(meta[key])[:10]
    text = f"{ch.get('title') or ''}\n{ch.get('content') or ''}"
    m = DATE_RE.search(text)
    return m.group("date") if m else None


def _is_result_chunk(ch: dict[str, Any]) -> bool:
    if ch.get("source_id") not in RESULT_SOURCES:
        return False
    meta = ch.get("metadata") or {}
    if meta.get("artefact") == "results_race":
        return True
    content = str(ch.get("content") or "")
    return "單場賽果" in content or "正式賽果" in content


def _has_placed_horse(ch: dict[str, Any]) -> bool:
    for m in extract_mentions(ch):
        if m.kind == "horse" and m.place:
            return True
    return False


def list_green_days(
    chunks: list[dict[str, Any]] | None = None,
    *,
    lookback_days: int = 5,
    max_days: int = 2,
    only_date: str | None = None,
) -> list[str]:
    docs = chunks if chunks is not None else load_all_chunks()
    today = today_hk()
    by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ch in docs:
        d = _chunk_date(ch)
        if not d:
            continue
        if d > today:
            continue
        by_date[d].append(ch)

    green: list[str] = []
    for d in sorted(by_date, reverse=True):
        if only_date and d != only_date:
            continue
        if lookback_days and d < _shift_days(today, -lookback_days):
            continue
        day_chunks = by_date[d]
        if not any(_is_result_chunk(ch) and _has_placed_horse(ch) for ch in day_chunks):
            continue
        green.append(d)
        if not only_date and len(green) >= max_days:
            break
    return green


def _shift_days(iso: str, delta: int) -> str:
    from datetime import date

    d = date.fromisoformat(iso)
    return (d + timedelta(days=delta)).isoformat()


def collect_day(date: str, chunks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    docs = chunks if chunks is not None else load_all_chunks()
    day = [ch for ch in docs if _chunk_date(ch) == date]
    results: list[dict[str, Any]] = []
    preds: list[dict[str, Any]] = []
    venue = ""
    seen_r: set[str] = set()
    seen_p: set[str] = set()

    for ch in day:
        src = ch.get("source_id")
        meta = ch.get("metadata") or {}
        if meta.get("venue") and not venue:
            venue = str(meta.get("venue"))
        for m in extract_mentions(ch):
            if m.venue and not venue:
                venue = m.venue
            if m.kind != "horse":
                continue
            rec = {
                "name": m.name,
                "name_ch": m.name,
                "horse": m.name,
                "place": m.place,
                "race_no": m.race_no,
                "source_id": src,
            }
            if src in RESULT_SOURCES and m.place:
                if m.name in seen_r:
                    continue
                seen_r.add(m.name)
                results.append(rec)
            elif src in PRED_SOURCES or m.extras.get("role") == "prediction":
                if m.name in seen_p:
                    continue
                seen_p.add(m.name)
                preds.append(rec)

    results.sort(key=lambda r: int(r["place"]) if str(r.get("place") or "").isdigit() else 99)
    green = bool(results) and any(_is_result_chunk(ch) and _has_placed_horse(ch) for ch in day)
    return {
        "race_date": date,
        "venue": venue,
        "green": green,
        "results": results,
        "predictions": preds,
        "result_count": len(results),
        "prediction_count": len(preds),
    }


def reflect_completed(
    *,
    date: str | None = None,
    lookback_days: int = 5,
    max_days: int = 2,
    model_version: str | None = None,
    chunks: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    docs = chunks if chunks is not None else load_all_chunks()
    days = list_green_days(
        docs, lookback_days=lookback_days, max_days=max_days, only_date=date
    )
    if date and date not in days:
        return {
            "ok": False,
            "skipped": True,
            "reason": "no_green_results",
            "race_date": date,
            "days": [],
            "wrote": [],
        }
    if not days:
        return {
            "ok": True,
            "skipped": True,
            "reason": "no_green_results_in_window",
            "days": [],
            "wrote": [],
        }

    wrote: list[dict[str, Any]] = []
    for d in days:
        bag = collect_day(d, docs)
        if not bag["green"]:
            continue
        note = build_reflection_note(
            race_date=d,
            predictions=bag["predictions"],
            results=bag["results"],
            model_version=model_version or "tx-oracle-observation",
        )
        note["venue"] = bag.get("venue")
        note["prediction_missing"] = not bag["predictions"]
        out = write_reflection_to_wiki(note)
        wrote.append(out)

    try:
        from brain.compile import _refresh_hot

        _refresh_hot()
    except Exception:
        pass

    return {
        "ok": True,
        "skipped": False,
        "days": days,
        "wrote": wrote,
    }
