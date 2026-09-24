"""Deposit a human-approved voice sample into wiki/style/.

Does not publish. Does not invent copy. Empty input is refused.
"""

from __future__ import annotations

from pathlib import Path

from brain.extract import observation_hash
from brain.wiki import get_or_create, today_hk


def seed_style(
    *,
    title: str,
    body: str,
    source: str = "manual",
) -> dict:
    text = (body or "").strip()
    if len(text) < 40:
        return {"ok": False, "reason": "too_short", "path": None}
    page = get_or_create("style", title)
    page.meta["status"] = "sample"
    page.meta["updated"] = today_hk()
    page.add_source(source)
    if not (page.sections.get("結論") or "").strip():
        page.sections["結論"] = (
            f"- {today_hk()} · 人手認可聲線樣本。只供草稿對照，發佈要再批。"
        )
    digest = observation_hash("style", title, text[:200])
    wrote = page.append_observation(text.replace("\n", " ")[:800], digest)
    # Keep a readable copy under 來源 so draft jobs can quote paragraphs.
    src_sec = (page.sections.get("來源") or "").strip()
    block = f"### {today_hk()} \u00b7 {source}\n\n{text[:4000]}"
    if block not in src_sec:
        page.sections["來源"] = f"{src_sec}\n\n{block}".strip() if src_sec else block
    page.save()
    return {
        "ok": True,
        "wrote_observation": wrote,
        "path": str(page.path),
        "title": page.title,
        "status": page.meta.get("status"),
    }


def seed_style_file(path: Path, title: str | None = None) -> dict:
    if not path.exists():
        return {"ok": False, "reason": "missing_file", "path": str(path)}
    body = path.read_text(encoding="utf-8", errors="ignore")
    return seed_style(title=title or path.stem, body=body, source=str(path.name))
