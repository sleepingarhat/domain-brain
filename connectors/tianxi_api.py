"""Connector for tianxi-backend (TX-Oracle prediction API).

Endpoints used (from tianxi-backend README):
  GET /api/analyze/today-picks
  GET /api/analyze/top-picks?raceId=
  GET /api/analyze/hit-rate?date=

Base URL is configurable via source.config.base_url
(e.g. https://tianxi-backend.<subdomain>.workers.dev).
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
                "(e.g. https://tianxi-backend.xxx.workers.dev)"
            )
        self.client = client or httpx.Client(timeout=45.0, follow_redirects=True)

    def _get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = f"{self.base}/{path.lstrip('/')}"
        resp = self.client.get(url, params=params or {})
        resp.raise_for_status()
        return resp.json()

    def fetch_today_picks(self) -> Any:
        return self._get_json("/api/analyze/today-picks")

    def fetch_top_picks(self, race_id: str) -> Any:
        return self._get_json("/api/analyze/top-picks", params={"raceId": race_id})

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

            # Normalise into readable knowledge chunks
            if isinstance(data, dict):
                races = data.get("races") or data.get("picks") or [data]
            elif isinstance(data, list):
                races = data
            else:
                races = [{"raw": data}]

            for i, race in enumerate(races[:20]):
                title = (
                    f"TX-Oracle today picks #{i+1}"
                    if not isinstance(race, dict)
                    else race.get("raceId")
                    or race.get("race_id")
                    or race.get("name")
                    or f"race-{i+1}"
                )
                body = json.dumps(race, ensure_ascii=False, indent=2, default=str)
                chunks.append(
                    {
                        "source_id": self.source.id,
                        "title": str(title),
                        "content": body[:8000],
                        "content_hash": _content_hash(body),
                        "metadata": {
                            "endpoint": "/api/analyze/today-picks",
                            "index": i,
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
