"""Markdown wiki pages with YAML frontmatter. Knowledge layer only."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WIKI_DIR = ROOT / "wiki"
HK_TZ = timezone(timedelta(hours=8))

FM_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)

TYPE_DIR = {
    "horse": WIKI_DIR / "entities" / "horses",
    "jockey": WIKI_DIR / "entities" / "jockeys",
    "trainer": WIKI_DIR / "entities" / "trainers",
    "course": WIKI_DIR / "entities" / "courses",
    "concept": WIKI_DIR / "concepts",
    "source": WIKI_DIR / "sources",
    "synthesis": WIKI_DIR / "synthesis",
    "style": WIKI_DIR / "style",
    "index": WIKI_DIR,
    "log": WIKI_DIR,
}

SECTIONS = ("結論", "觀察", "矛盾", "來源")


def today_hk() -> str:
    return datetime.now(HK_TZ).date().isoformat()


def slugify(name: str) -> str:
    text = (name or "").strip()
    text = re.sub(r"[\\/:*?\"<>|]+", "-", text)
    text = re.sub(r"\s+", "-", text)
    text = text.strip("-")
    return text[:80] or "untitled"


def _parse_scalar(raw: str) -> Any:
    raw = raw.strip()
    if raw in ("[]",):
        return []
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    return raw


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    meta: dict[str, Any] = {}
    current_list: str | None = None
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        if current_list and line.startswith("  - "):
            meta.setdefault(current_list, []).append(line[4:].strip())
            continue
        current_list = None
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            current_list = key
            meta[key] = []
            continue
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            meta[key] = [p.strip().strip("'\"") for p in inner.split(",") if p.strip()]
        else:
            meta[key] = _parse_scalar(val)
    body = text[m.end() :]
    return meta, body


def dump_frontmatter(meta: dict[str, Any]) -> str:
    order = ["type", "id", "title", "aliases", "sources", "updated", "status", "layer"]
    keys = order + [k for k in meta if k not in order]
    lines = ["---"]
    for k in keys:
        if k not in meta:
            continue
        v = meta[k]
        if isinstance(v, list):
            if not v:
                lines.append(f"{k}: []")
            else:
                lines.append(f"{k}:")
                for item in v:
                    lines.append(f"  - {item}")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def split_sections(body: str) -> dict[str, str]:
    found: dict[str, str] = {s: "" for s in SECTIONS}
    current: str | None = None
    preamble: list[str] = []
    buf: list[str] = []

    def flush() -> None:
        if current:
            found[current] = "\n".join(buf).strip()

    for line in body.splitlines():
        heading = line.strip()
        if heading.startswith("## ") and heading[3:].strip() in SECTIONS:
            flush()
            current = heading[3:].strip()
            buf = []
            continue
        if current is None:
            preamble.append(line)
        else:
            buf.append(line)
    flush()
    found["_preamble"] = "\n".join(preamble).strip()
    return found


def join_sections(title: str, sections: dict[str, str]) -> str:
    parts = [f"# {title}", ""]
    pre = sections.get("_preamble") or ""
    pre_lines = [ln for ln in pre.splitlines() if not ln.startswith("# ")]
    pre = "\n".join(pre_lines).strip()
    if pre:
        parts.extend([pre, ""])
    for name in SECTIONS:
        parts.append(f"## {name}")
        parts.append("")
        body = (sections.get(name) or "").strip() or ("（未有）" if name == "矛盾" else "")
        parts.append(body)
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


@dataclass
class WikiPage:
    path: Path
    meta: dict[str, Any] = field(default_factory=dict)
    sections: dict[str, str] = field(default_factory=dict)

    @property
    def title(self) -> str:
        return str(self.meta.get("title") or self.path.stem)

    def text(self) -> str:
        return dump_frontmatter(self.meta) + "\n" + join_sections(self.title, self.sections)

    def save(self) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(self.text(), encoding="utf-8")
        return self.path

    def observation_hashes(self) -> set[str]:
        out: set[str] = set()
        for line in (self.sections.get("觀察") or "").splitlines():
            if "· hash:" in line:
                out.add(line.rsplit("· hash:", 1)[-1].strip())
        return out

    def append_observation(self, line: str, digest: str) -> bool:
        if digest in self.observation_hashes():
            return False
        existing = (self.sections.get("觀察") or "").strip()
        entry = f"- {line} · hash:{digest}"
        self.sections["觀察"] = f"{existing}\n{entry}".strip() if existing else entry
        return True

    def append_contradiction(self, line: str) -> None:
        existing = (self.sections.get("矛盾") or "").strip()
        if existing in ("", "（未有）"):
            self.sections["矛盾"] = f"- {line}"
            return
        if line in existing:
            return
        self.sections["矛盾"] = f"{existing}\n- {line}"

    def add_source(self, source_id: str) -> None:
        srcs = list(self.meta.get("sources") or [])
        if source_id and source_id not in srcs:
            srcs.append(source_id)
            self.meta["sources"] = srcs
        sources_sec = (self.sections.get("來源") or "").strip()
        mark = f"- [[{source_id}]]"
        if source_id and mark not in sources_sec:
            if sources_sec in ("", "（未有）"):
                self.sections["來源"] = mark
            else:
                self.sections["來源"] = f"{sources_sec}\n{mark}"


def load_page(path: Path) -> WikiPage | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    return WikiPage(path=path, meta=meta, sections=split_sections(body))


def page_path(page_type: str, title: str) -> Path:
    folder = TYPE_DIR[page_type]
    if page_type == "index":
        return WIKI_DIR / "index.md"
    if page_type == "log":
        return WIKI_DIR / "log.md"
    return folder / f"{slugify(title)}.md"


def get_or_create(page_type: str, title: str, page_id: str | None = None) -> WikiPage:
    path = page_path(page_type, title)
    existing = load_page(path)
    if existing:
        return existing
    meta = {
        "type": page_type,
        "id": page_id or f"{page_type}-{slugify(title).lower()}",
        "title": title,
        "aliases": [],
        "sources": [],
        "updated": today_hk(),
        "status": "active",
        "layer": "project" if page_type == "synthesis" else "knowledge",
    }
    sections = {s: "" for s in SECTIONS}
    sections["矛盾"] = "（未有）"
    sections["_preamble"] = ""
    return WikiPage(path=path, meta=meta, sections=sections)


def iter_pages(wiki_dir: Path | None = None) -> list[WikiPage]:
    root = wiki_dir or WIKI_DIR
    if not root.exists():
        return []
    pages: list[WikiPage] = []
    for path in sorted(root.rglob("*.md")):
        if path.name.upper() in {"RULES.MD", "README.MD"}:
            continue
        page = load_page(path)
        if page:
            pages.append(page)
    return pages


def wiki_as_docs(wiki_dir: Path | None = None) -> list[dict[str, Any]]:
    """Flatten wiki pages into BM25 documents."""
    docs: list[dict[str, Any]] = []
    for page in iter_pages(wiki_dir):
        body = "\n".join(
            [
                page.title,
                page.sections.get("結論") or "",
                page.sections.get("觀察") or "",
                page.sections.get("矛盾") or "",
            ]
        ).strip()
        if not body:
            continue
        docs.append(
            {
                "id": f"wiki:{page.path.relative_to(wiki_dir or WIKI_DIR)}",
                "source_id": "wiki",
                "title": page.title,
                "content": body[:12000],
                "content_hash": page.meta.get("id") or page.path.stem,
                "metadata": {
                    "kind": "wiki",
                    "type": page.meta.get("type"),
                    "path": str(page.path.relative_to(ROOT)),
                    "layer": page.meta.get("layer"),
                },
                "race_date": None,
            }
        )
    return docs
