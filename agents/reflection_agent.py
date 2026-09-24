"""Reflection agent — compare predictions vs results and write wiki notes.

Writes dated observations onto synthesis + mentioned horse pages.
Does not overwrite conclusions. Optional Mem0 payload remains available.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from brain.extract import observation_hash
from brain.wiki import get_or_create, today_hk


def build_reflection_note(
    *,
    race_date: str,
    predictions: list[dict[str, Any]],
    results: list[dict[str, Any]],
    model_version: str | None = None,
) -> dict[str, Any]:
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


def write_reflection_to_wiki(note: dict[str, Any]) -> dict[str, Any]:
    race_date = str(note.get("race_date") or today_hk())
    model_version = note.get("model_version") or "unknown"
    predicted = [str(x) for x in (note.get("predicted") or [])]
    actual = [str(x) for x in (note.get("actual_sample") or [])]
    overlap = note.get("overlap")
    written: list[str] = []

    syn = get_or_create("synthesis", f"race-{race_date}", page_id=f"synthesis-{race_date}")
    syn.meta["title"] = f"賽日 {race_date}"
    line = (
        f"{race_date} · reflection · model={model_version} "
        f"預測[{', '.join(predicted) or 'n/a'}] "
        f"賽果樣本[{', '.join(actual) or 'n/a'}] overlap={overlap}"
    )
    digest = observation_hash("synthesis", race_date, str(model_version), line)
    if syn.append_observation(line, digest):
        if not (syn.sections.get("結論") or "").strip():
            syn.sections["結論"] = (
                f"- {race_date} · 賽日紜合頁（項目層）。預測同賽果並記，唔互相覆蓋。"
            )
        if predicted and actual and set(predicted).isdisjoint(set(actual)):
            syn.append_contradiction(
                f"{race_date} · 預測名單同賽果樣本無重叠（model={model_version}）"
            )
        syn.add_source("reflection")
        syn.meta["updated"] = today_hk()
        syn.save()
        written.append(str(syn.path))

    names = list(dict.fromkeys(predicted + actual))
    for name in names:
        if not name or name in ("n/a",):
            continue
        page = get_or_create("horse", name)
        role = "預測" if name in predicted else "賽果"
        if name in predicted and name in actual:
            role = "預測且上名"
        hline = f"{race_date} · reflection · {role} · model={model_version} overlap={overlap}"
        hdig = observation_hash("horse", name, race_date, hline)
        if page.append_observation(hline, hdig):
            page.add_source("reflection")
            page.meta["updated"] = today_hk()
            if name in predicted and name not in actual:
                page.append_contradiction(
                    f"{race_date} · 入選預測但未見於賽果樣本（model={model_version}）"
                )
            page.save()
            written.append(str(page.path))

    bias = get_or_create("concept", "冷熱偏")
    bline = f"{race_date} · reflection · overlap={overlap} model={model_version}"
    if bias.append_observation(bline, observation_hash("concept", "冷熱偏", race_date, bline)):
        bias.meta["updated"] = today_hk()
        bias.save()
        written.append(str(bias.path))

    return {"pages": written, "race_date": race_date}


def reflection_to_mem0_payload(
    note: dict[str, Any], user_id: str = "tianxi-brain"
) -> dict[str, Any]:
    return {
        "messages": [{"role": "assistant", "content": note.get("summary") or str(note)}],
        "user_id": user_id,
        "metadata": {
            "type": "race_reflection",
            "race_date": note.get("race_date"),
            "model_version": note.get("model_version"),
        },
    }
