"""Compile ingestion chunks into wiki entity pages.

Ingest without a linked observation is not finished.
Never overwrite conclusions; contradictions are appended.
"""

from __future__ import annotations

from typing import Any

from brain.extract import Mention, extract_mentions, observation_hash
from brain.store import load_all_chunks
from brain.wiki import WIKI_DIR, WikiPage, get_or_create, iter_pages, today_hk

KIND_TO_TYPE = {
    "horse": "horse",
    "jockey": "jockey",
    "trainer": "trainer",
    "course": "course",
    "source": "source",
}

MAX_OBS = 40
META_TYPES = {"index", "log", "meta", "hot", "style"}


def _obs_line(m: Mention) -> str:
    when = m.race_date or today_hk()
    src = m.source_id or "unknown"
    role = m.extras.get("role")
    tag = "預測" if role == "prediction" or src == "tianxi-api" else "賽果"
    extra = ""
    if m.kind == "horse":
        bits = []
        if m.place:
            bits.append(f"第{m.place}名")
        if m.extras.get("jockey"):
            bits.append(f"騎師 [[{m.extras['jockey']}]]")
        if m.extras.get("trainer"):
            bits.append(f"練馬師 [[{m.extras['trainer']}]]")
        extra = " ".join(bits)
    elif m.kind in ("jockey", "trainer") and m.extras.get("horse"):
        extra = f"馬 [[{m.extras['horse']}]]"
        if m.place:
            extra += f" 第{m.place}名"
    loc = ""
    if m.venue:
        loc = f" [[{m.venue}]]"
    if m.race_no:
        loc += f" R{m.race_no}"
    snippet = (m.snippet or "").replace("\n", " ")[:120]
    return f"{when} · {src} · {tag}{loc} {extra} — {snippet}".strip()


def _trim_observations(page: WikiPage) -> None:
    raw = page.sections.get("觀察") or ""
    lines = [ln for ln in raw.splitlines() if ln.strip()]
    if len(lines) <= MAX_OBS:
        return
    keep = lines[-MAX_OBS:]
    overflow = len(lines) - MAX_OBS
    page.sections["觀察"] = f"（較早 {overflow} 條觀察已截斷，矛盾區保留）\n" + "\n".join(keep)


def _seed_conclusion(page: WikiPage, m: Mention) -> None:
    existing = (page.sections.get("結論") or "").strip()
    if existing:
        return
    if m.kind == "course":
        page.sections["結論"] = f"- {today_hk()} · 場地頁已開。賽果只 append 觀察，唔改呢句。"
    elif m.extras.get("role") == "prediction" or m.source_id == "tianxi-api":
        page.sections["結論"] = (
            f"- {today_hk()} · 本頁含 TX-Oracle 預測觀察，預測唔等於完場事實。"
        )
    else:
        page.sections["結論"] = f"- {today_hk()} · 由賽果／評述首次提及，結論待更多場次先收窄。"


def compile_chunks(chunks: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    docs = chunks if chunks is not None else load_all_chunks()
    created = 0
    updated_pages: set[str] = set()
    observations = 0
    skipped = 0
    cache: dict[tuple[str, str], WikiPage] = {}

    for ch in docs:
        mentions = extract_mentions(ch)
        if not mentions:
            skipped += 1
            continue
        for m in mentions:
            page_type = KIND_TO_TYPE.get(m.kind)
            if not page_type:
                continue
            key = (page_type, m.name)
            page = cache.get(key) or get_or_create(page_type, m.name)
            is_new = not page.path.exists()
            line = _obs_line(m)
            digest = observation_hash(
                m.kind, m.name, m.race_date or "", m.source_id or "", m.snippet or line
            )
            wrote = page.append_observation(line, digest)
            cache[key] = page
            if not wrote:
                continue
            observations += 1
            page.add_source(m.source_id or "")
            page.meta["updated"] = today_hk()
            _seed_conclusion(page, m)
            if m.source_id == "tianxi-api":
                page.append_contradiction(
                    f"{m.race_date or today_hk()} · tianxi-api 預測觀察，尚未用賽果核對"
                )
            _trim_observations(page)
            page.save()
            if is_new:
                created += 1
            updated_pages.add(str(page.path))

    _refresh_index()
    _append_log(
        created=created,
        updated=len(updated_pages),
        observations=observations,
        chunks=len(docs),
    )
    _refresh_hot()
    return {
        "chunks": len(docs),
        "pages_touched": len(updated_pages),
        "created": created,
        "updated": len(updated_pages),
        "observations": observations,
        "unlinked_chunks": skipped,
        "wiki": str(WIKI_DIR),
    }


def _refresh_index() -> None:
    index_path = WIKI_DIR / "index.md"
    if not index_path.exists():
        return
    pages = [
        p
        for p in iter_pages()
        if p.meta.get("type") in ("horse", "jockey", "trainer", "course", "concept", "synthesis")
    ]
    pages.sort(key=lambda p: str(p.meta.get("updated") or ""), reverse=True)
    lines = [
        f"- [[{p.path.stem}]]（{p.meta.get('type')} · {p.meta.get('updated')}）"
        for p in pages[:40]
    ]
    marker = "<!-- COMPILE:PAGES -->"
    raw = index_path.read_text(encoding="utf-8")
    if marker not in raw:
        return
    head, _, _ = raw.partition(marker)
    index_path.write_text(head + marker + "\n" + "\n".join(lines) + "\n", encoding="utf-8")


def _append_log(**counts: Any) -> None:
    path = WIKI_DIR / "log.md"
    if not path.exists():
        return
    line = (
        f"- {today_hk()} · chunks={counts.get('chunks')} "
        f"created={counts.get('created')} updated={counts.get('updated')} "
        f"obs={counts.get('observations')}"
    )
    text = path.read_text(encoding="utf-8")
    marker = "<!-- COMPILE:LOG -->"
    if marker in text:
        path.write_text(text.replace(marker, marker + "\n" + line, 1), encoding="utf-8")
        return
    path.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8")


def _replace_marker(text: str, marker: str, block: str) -> str:
    if marker not in text:
        return text
    head, _, tail = text.partition(marker)
    # Drop previous auto block until next heading or EOF.
    rest = tail.lstrip("\n")
    cut = rest.find("\n## ")
    if cut == -1:
        cut = rest.find("\n### ")
    leftover = rest[cut:] if cut != -1 else ""
    return head + marker + "\n" + block.rstrip() + "\n" + leftover


def _refresh_hot() -> None:
    path = WIKI_DIR / "hot.md"
    if not path.exists():
        return
    contradictions: list[str] = []
    for page in iter_pages():
        if page.meta.get("type") in META_TYPES:
            continue
        body = (page.sections.get("矛盾") or "").strip()
        if body in ("", "（未有）"):
            continue
        for ln in body.splitlines():
            s = ln.strip()
            if s.startswith("- "):
                contradictions.append(f"- [[{page.path.stem}]] {s[2:]}")
    contradictions = contradictions[-8:]
    contra_block = "\n".join(contradictions) if contradictions else "（未有未結矛盾）"

    log_path = WIKI_DIR / "log.md"
    log_lines: list[str] = []
    if log_path.exists():
        for ln in log_path.read_text(encoding="utf-8").splitlines():
            if ln.startswith("- ") and "chunks=" in ln:
                log_lines.append(ln)
    log_block = "\n".join(log_lines[:5]) if log_lines else "（尚未 compile）"

    text = path.read_text(encoding="utf-8")
    text = _replace_marker(text, "<!-- HOT:CONTRADICTIONS -->", contra_block)
    text = _replace_marker(text, "<!-- HOT:LOG -->", log_block)
    text = text.replace("updated: 2026-09-24", f"updated: {today_hk()}")
    if "updated:" in text.split("---", 2)[1] if text.startswith("---") else "":
        pass
    path.write_text(text, encoding="utf-8")
