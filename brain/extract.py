"""Pull horse / jockey / trainer / course mentions out of ingestion chunks."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any

PLACE_LINE = re.compile(
    r"第(?P<place>\d+)\s*名\s+(?:(?P<no>\d+)\s*號\s+)?(?P<horse>[^\s騎第]+)"
)
JOCKEY_RE = re.compile(r"騎師[:：]\s*(?P<name>[^\s練獨\n]+)")
TRAINER_RE = re.compile(r"練馬師[:：]\s*(?P<name>[^\s獨\n]+)")
VENUE_RE = re.compile(r"場地[:：]\s*(?P<name>[^\s\n]+)")
DATE_RE = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2})")
RACE_RE = re.compile(r"第\s*(?P<n>\d+)\s*場")

VENUE_ALIAS = {
    "跑馬地": "跑馬地",
    "谷": "跑馬地",
    "happyvalley": "跑馬地",
    "hv": "跑馬地",
    "沙田": "沙田",
    "st": "沙田",
    "sha tin": "沙田",
    "田": "沙田",
}

SKIP_NAMES = {"", "?", "n/a", "None", "null", "騎師", "練馬師", "場地"}


def _clean_name(name: str) -> str:
    name = (name or "").strip().strip("，,。．.、")
    name = re.sub(r"^(號|第)", "", name)
    return name.strip()


def _norm_venue(raw: str) -> str | None:
    key = (raw or "").strip().lower().replace(" ", "")
    if not key:
        return None
    if raw.strip() in VENUE_ALIAS:
        return VENUE_ALIAS[raw.strip()]
    return VENUE_ALIAS.get(key, raw.strip() if raw.strip() else None)


def observation_hash(*parts: str) -> str:
    blob = "|".join(parts)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


@dataclass
class Mention:
    kind: str
    name: str
    race_date: str | None = None
    venue: str | None = None
    race_no: str | None = None
    place: str | None = None
    source_id: str | None = None
    snippet: str = ""
    extras: dict[str, str] = field(default_factory=dict)


def extract_mentions(chunk: dict[str, Any]) -> list[Mention]:
    title = str(chunk.get("title") or "")
    content = str(chunk.get("content") or "")
    text = f"{title}\n{content}"
    source_id = chunk.get("source_id")
    race_date = chunk.get("race_date")
    if not race_date:
        dm = DATE_RE.search(text)
        race_date = dm.group("date") if dm else None
    venue = None
    vm = VENUE_RE.search(text)
    if vm:
        venue = _norm_venue(vm.group("name"))
    meta = chunk.get("metadata") or {}
    if not venue and meta.get("venue"):
        venue = _norm_venue(str(meta.get("venue")))
    race_no = None
    rm = RACE_RE.search(text)
    if rm:
        race_no = rm.group("n")
    elif meta.get("race_no") is not None:
        race_no = str(meta.get("race_no"))

    mentions: list[Mention] = []
    seen: set[tuple[str, str]] = set()

    def add(m: Mention) -> None:
        name = _clean_name(m.name)
        if name in SKIP_NAMES or len(name) < 2:
            return
        key = (m.kind, name)
        if key in seen:
            return
        seen.add(key)
        m.name = name
        mentions.append(m)

    for line in text.splitlines():
        pm = PLACE_LINE.search(line)
        if not pm:
            continue
        horse = _clean_name(pm.group("horse"))
        jm = JOCKEY_RE.search(line)
        tm = TRAINER_RE.search(line)
        jockey = _clean_name(jm.group("name")) if jm else ""
        trainer = _clean_name(tm.group("name")) if tm else ""
        place = pm.group("place")
        snippet = line.strip()[:200]
        add(
            Mention(
                kind="horse",
                name=horse,
                race_date=race_date,
                venue=venue,
                race_no=race_no,
                place=place,
                source_id=source_id,
                snippet=snippet,
                extras={"jockey": jockey, "trainer": trainer},
            )
        )
        if jockey:
            add(
                Mention(
                    kind="jockey",
                    name=jockey,
                    race_date=race_date,
                    venue=venue,
                    race_no=race_no,
                    place=place,
                    source_id=source_id,
                    snippet=snippet,
                    extras={"horse": horse},
                )
            )
        if trainer:
            add(
                Mention(
                    kind="trainer",
                    name=trainer,
                    race_date=race_date,
                    venue=venue,
                    race_no=race_no,
                    place=place,
                    source_id=source_id,
                    snippet=snippet,
                    extras={"horse": horse},
                )
            )

    pick_re = re.compile(
        r"-\s*(?P<no>\d+)\s*號\s+(?P<horse>[^\s騎]+)\s+騎師:(?P<jockey>[^\s]+)\s+練馬師:(?P<trainer>[^\s]+)"
    )
    for m in pick_re.finditer(text):
        add(
            Mention(
                kind="horse",
                name=m.group("horse"),
                race_date=race_date,
                venue=venue,
                race_no=race_no,
                source_id=source_id,
                snippet=m.group(0)[:200],
                extras={
                    "jockey": _clean_name(m.group("jockey")),
                    "trainer": _clean_name(m.group("trainer")),
                    "role": "prediction",
                },
            )
        )

    if venue:
        add(
            Mention(
                kind="course",
                name=venue,
                race_date=race_date,
                venue=venue,
                race_no=race_no,
                source_id=source_id,
                snippet=f"{race_date or ''} {venue} R{race_no or '?'}",
            )
        )

    if "TX-Oracle" in text or source_id == "tianxi-api":
        add(
            Mention(
                kind="source",
                name="tianxi-api",
                race_date=race_date,
                venue=venue,
                source_id=source_id,
                snippet="TX-Oracle 預測觀察",
                extras={"role": "prediction"},
            )
        )
    if source_id == "tianxi-database":
        add(
            Mention(
                kind="source",
                name="tianxi-database",
                race_date=race_date,
                venue=venue,
                source_id=source_id,
                snippet="正式賽果",
            )
        )

    return mentions
