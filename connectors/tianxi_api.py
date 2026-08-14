"""Connector for tianxi-backend (TX-Oracle prediction API).

Endpoints used:
  GET /api/analyze/today-picks
  GET /api/analyze/top-picks?raceId=
  GET /api/analyze/hit-rate?date=

Base URL via source.config.base_url (e.g. https://www.tianxi.racing).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from ingestion.models import CrawlRun, RunStatus, Source

HK_TZ = timezone(timedelta(hours=8))


def _now_hk() -> datetime:
    return datetime.now(HK_TZ)


def _make_run_id(source_id: str, started: datetime) -> str:
    return f"{started.strftime('%Y%m%d-%H%M%S')}-{source_id}"


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _summarize_race(race: dict[str, Any], meta: dict[str, Any] | None = None) -> str:
    """Human-readable Chinese summary for BM25 / RAG."""
    meta = meta or {}
    date = meta.get("date") or race.get("date") or ""
    venue = meta.get("venue") or race.get("venue") or ""
    lines = [
        f"TX-Oracle 預測摘要",
        f"日期: {date}  場地: {venue}",
        f"場次: {race.get('raceNumber') or race.get('race_number') or '?'}",
        f"賽名: {race.get('title') or ''}",
        f"班次: {race.get('class') or ''}  途程: {race.get('distance') or ''}  "
        f"地質: {race.get('going') or meta.get('trackCondition') or ''}",
        f"raceId: {race.get('raceId') or race.get('race_id') or ''}",
        "精選馬:",
    ]
    picks = race.get("picks") or []
    if isinstance(picks, list):
        for p in picks[:8]:
            if not isinstance(p, dict):
                continue
            lines.append(
                f"- {p.get('horseNumber') or p.get('number') or '?'}號 "
                f"{p.get('nameCh') or p.get('name') or ''} "
                f"騎師:{p.get('jockeyCh') or p.get('jockey') or ''} "
                f"練馬師:{p.get('trainerCh') or p.get('trainer') or ''} "
                f"檔:{p.get('draw') or ''}"
            )
    # keep a short JSON tail for structured fans
    lines.append("\n--- raw picks (截斷) ---")
    lines.append(json.dumps(picks[:5], ensure_ascii=False, default=str)[:2000])
    return "\n".join(lines)


class TianxiApiConnector:
    def __init__(self, source: Source, client: httpx.Client | None = None):
        if source.type.value != "api":
            raise ValueError(f"Expected type=api, got {source.type}")
        self.source = source
        self.base = (
            source.config.get("base_url")
            or source.url
            or ""
        ).rstrip("/")
        if not self.base:
            raise ValueError(
                "tianxi-api source requires config.base_url "
                "(e.g. https://www.tianxi.racing)"
            )
        self.client = client or httpx.Client(timeout=45.0, follow_redirects=True)

    def _get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base}/{path.lstrip('/')}"
        resp = self.client.get(url, params=params or {})
        resp.raise_for_status()
        return resp.json()

    def fetch_today_picks(self) -> Any:
        return self._get_json("/api/analyze/today-picks")

    def run(self) -> tuple[CrawlRun, list[dict[str, Any]]]:
        started = _now_hk()
        run_id = _make_run_id(self.source.id, started)
        chunks: list[dict[str, Any]] = []
        items_fetched = 0
        items_new = 0
        error_message: str | None = None
        status = RunStatus.SUCCESS
        content_hash: str | None = None

        try:
            data = self.fetch_today_picks()
            raw = json.dumps(data, ensure_ascii=False, default=str)
            content_hash = _content_hash(raw)
            items_fetched = 1

            meta: dict[str, Any] = {}
            if isinstance(data, dict):
                meta = {
                    "date": data.get("date"),
                    "venue": data.get("venue"),
                    "trackCondition": data.get("trackCondition"),
                }
                races = data.get("races") or data.get("picks") or [data]
            elif isinstance(data, list):
                races = data
            else:
                races = [{"raw": data}]

            for i, race in enumerate(races[:20]):
                if not isinstance(race, dict):
                    continue
                title = (
                    race.get("raceId")
                    or race.get("race_id")
                    or race.get("title")
                    or f"race-{i+1}"
                )
                body = _summarize_race(race, meta)
                chunks.append(
                    {
                        "source_id": self.source.id,
                        "title": str(title),
                        "content": body[:8000],
                        "content_hash": _content_hash(body),
                        "metadata": {
                            "endpoint": "/api/analyze/today-picks",
                            "index": i,
                            **{k: v for k, v in meta.items() if v is not None},
                        },
                    }
                )
                items_new += 1

            if not chunks:
                chunks.append(
                    {
                        "source_id": self.source.id,
                        "title": "TX-Oracle today-picks (raw)",
                        "content": raw[:8000],
                        "content_hash": content_hash,
                        "metadata": {"endpoint": "/api/analyze/today-picks"},
                    }
                )
                items_new = 1

        except Exception as e:  # noqa: BLE001
            status = RunStatus.FAILED
            error_message = str(e)

        finished = _now_hk()
        run = CrawlRun(
            run_id=run_id,
            source_id=self.source.id,
            started_at=started,
            finished_at=finished,
            status=status,
            items_fetched=items_fetched,
            items_new=items_new,
            items_updated=0,
            items_skipped=0,
            error_message=error_message,
            duration_seconds=round((finished - started).total_seconds(), 2),
            content_hash=content_hash,
            metadata={"base_url": self.base},
        )
        return run, chunks
