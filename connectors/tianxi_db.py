"""Connector for tianxi-database (structured HKJC race data via raw GitHub CSVs).

Does NOT re-scrape HKJC. Consumes the already-maintained artefacts from
https://github.com/sleepingarhat/tianxi-database
"""

from __future__ import annotations

import hashlib
import io
from datetime import date, datetime, timedelta, timezone
from typing import Any

import httpx
import pandas as pd

from ingestion.models import CrawlRun, RunStatus, Source

HK_TZ = timezone(timedelta(hours=8))


def _now_hk() -> datetime:
    return datetime.now(HK_TZ)


def _make_run_id(source_id: str, started: datetime) -> str:
    return f"{started.strftime('%Y%m%d-%H%M%S')}-{source_id}"


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class TianxiDbConnector:
    """Fetch structured race data from tianxi-database raw CSVs."""

    def __init__(self, source: Source, client: httpx.Client | None = None):
        if source.type.value != "database":
            raise ValueError(f"Expected type=database, got {source.type}")
        self.source = source
        self.base = (
            source.config.get("base_raw_url")
            or source.url
            or "https://raw.githubusercontent.com/sleepingarhat/tianxi-database/main"
        ).rstrip("/")
        self.client = client or httpx.Client(timeout=30.0, follow_redirects=True)

    def _fetch_text(self, path: str) -> str:
        url = f"{self.base}/{path.lstrip('/')}"
        resp = self.client.get(url)
        resp.raise_for_status()
        return resp.text

    def fetch_results_for_date(self, race_date: date) -> pd.DataFrame | None:
        """Fetch results_YYYY-MM-DD.csv for a single race day. Returns None if 404."""
        year = race_date.year
        fname = f"data/{year}/results_{race_date.isoformat()}.csv"
        try:
            text = self._fetch_text(fname)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        df = pd.read_csv(io.StringIO(text), encoding="utf-8-sig")
        return df

    def run(
        self,
        lookback_days: int = 7,
        max_days: int = 5,
    ) -> tuple[CrawlRun, list[dict[str, Any]]]:
        """
        Pull recent race-day results CSVs and return (CrawlRun, list of chunk dicts).

        Each chunk is a simple knowledge unit ready for downstream RAG / Mem0.
        """
        started = _now_hk()
        run_id = _make_run_id(self.source.id, started)
        chunks: list[dict[str, Any]] = []
        items_fetched = 0
        items_new = 0
        errors: list[str] = []
        hashes: list[str] = []

        today = started.date()
        checked = 0
        d = today
        while checked < lookback_days and items_fetched < max_days:
            try:
                df = self.fetch_results_for_date(d)
                if df is not None and not df.empty:
                    items_fetched += 1
                    # Simple text summary as knowledge chunk (MVP)
                    summary = (
                        f"Race day {d.isoformat()} — {len(df)} runners.\n"
                        f"Columns: {', '.join(df.columns[:12])}...\n"
                        f"Sample (first 3 rows):\n{df.head(3).to_string(index=False)}"
                    )
                    h = _content_hash(summary)
                    hashes.append(h)
                    chunks.append(
                        {
                            "source_id": self.source.id,
                            "race_date": d.isoformat(),
                            "title": f"HKJC Results {d.isoformat()}",
                            "content": summary,
                            "content_hash": h,
                            "row_count": len(df),
                            "metadata": {
                                "artefact": "results",
                                "year": d.year,
                            },
                        }
                    )
                    items_new += 1  # MVP: treat every successful fetch as new
                checked += 1
            except Exception as e:  # noqa: BLE001
                errors.append(f"{d.isoformat()}: {e}")
            d = d - timedelta(days=1)

        finished = _now_hk()
        duration = (finished - started).total_seconds()

        if errors and items_fetched == 0:
            status = RunStatus.FAILED
            error_message = "; ".join(errors[:3])
        elif errors:
            status = RunStatus.PARTIAL
            error_message = "; ".join(errors[:3])
        else:
            status = RunStatus.SUCCESS
            error_message = None

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
            duration_seconds=round(duration, 2),
            content_hash="|".join(hashes) if hashes else None,
            metadata={
                "lookback_days": lookback_days,
                "max_days": max_days,
                "base_url": self.base,
            },
        )
        return run, chunks
