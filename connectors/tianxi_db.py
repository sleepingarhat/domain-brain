"""Connector for tianxi-database (structured HKJC race data via raw GitHub CSVs).

Does NOT re-scrape HKJC. Consumes artefacts from
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


def _col(df: pd.DataFrame, *names: str) -> str | None:
    lower = {c.lower(): c for c in df.columns}
    for n in names:
        if n.lower() in lower:
            return lower[n.lower()]
    return None


def _summarize_race_day(d: date, df: pd.DataFrame) -> list[dict[str, Any]]:
    """Emit one day overview + per-race Chinese summaries (better BM25)."""
    chunks: list[dict[str, Any]] = []

    c_venue = _col(df, "venue")
    c_race = _col(df, "race_no", "race_number")
    c_name = _col(df, "race_name", "title")
    c_class = _col(df, "race_class", "class")
    c_dist = _col(df, "distance_m", "distance")
    c_going = _col(df, "going")
    c_course = _col(df, "course")
    c_place = _col(df, "place", "finishing_position")
    c_hno = _col(df, "horse_no", "horse_number")
    c_hname = _col(df, "horse_name", "name_ch", "name")
    c_jockey = _col(df, "jockey", "jockey_name")
    c_trainer = _col(df, "trainer", "trainer_name")
    c_odds = _col(df, "win_odds", "odds")

    venue = str(df[c_venue].iloc[0]) if c_venue else ""
    n_races = int(df[c_race].nunique()) if c_race else 0

    day_lines = [
        f"香港賽馬 正式賽果摘要",
        f"日期: {d.isoformat()}",
        f"場地: {venue}",
        f"賽事場數: {n_races}",
        f"出賽馬匹紀錄行數: {len(df)}",
    ]
    if c_going:
        day_lines.append(f"地質示例: {df[c_going].dropna().astype(str).head(1).tolist()}")
    day_text = "\n".join(day_lines)
    chunks.append(
        {
            "source_id": "tianxi-database",
            "race_date": d.isoformat(),
            "title": f"賽果總覽 {d.isoformat()} {venue}",
            "content": day_text,
            "content_hash": _content_hash(day_text),
            "row_count": len(df),
            "metadata": {"artefact": "results_day", "year": d.year, "venue": venue},
        }
    )

    if not c_race:
        return chunks

    for race_no, g in df.groupby(c_race, sort=True):
        g = g.copy()
        race_name = str(g[c_name].iloc[0]) if c_name else ""
        klass = str(g[c_class].iloc[0]) if c_class else ""
        dist = str(g[c_dist].iloc[0]) if c_dist else ""
        going = str(g[c_going].iloc[0]) if c_going else ""
        course = str(g[c_course].iloc[0]) if c_course else ""

        lines = [
            f"香港賽馬 單場賽果",
            f"日期: {d.isoformat()}  場地: {venue}",
            f"第 {race_no} 場  {race_name}",
            f"班次: {klass}  途程: {dist}米  地質: {going}  賽道: {course}",
            "名次:",
        ]

        # sort by place if available
        if c_place:
            with pd.option_context("mode.chained_assignment", None):
                g["_place_num"] = pd.to_numeric(g[c_place], errors="coerce")
            g = g.sort_values("_place_num", na_position="last")

        for _, row in g.head(14).iterrows():
            place = row[c_place] if c_place else ""
            hno = row[c_hno] if c_hno else ""
            hname = row[c_hname] if c_hname else ""
            jockey = row[c_jockey] if c_jockey else ""
            trainer = row[c_trainer] if c_trainer else ""
            odds = row[c_odds] if c_odds else ""
            lines.append(
                f"- 第{place}名  {hno}號 {hname}  "
                f"騎師:{jockey}  練馬師:{trainer}  獨贏:{odds}"
            )

        body = "\n".join(lines)
        chunks.append(
            {
                "source_id": "tianxi-database",
                "race_date": d.isoformat(),
                "title": f"賽果 {d.isoformat()} R{race_no} {race_name}",
                "content": body,
                "content_hash": _content_hash(body),
                "row_count": len(g),
                "metadata": {
                    "artefact": "results_race",
                    "year": d.year,
                    "venue": venue,
                    "race_no": int(race_no) if str(race_no).isdigit() else race_no,
                },
            }
        )

    return chunks


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
        year = race_date.year
        fname = f"data/{year}/results_{race_date.isoformat()}.csv"
        try:
            text = self._fetch_text(fname)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        return pd.read_csv(io.StringIO(text), encoding="utf-8-sig")

    def run(
        self,
        lookback_days: int = 7,
        max_days: int = 5,
    ) -> tuple[CrawlRun, list[dict[str, Any]]]:
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
                    day_chunks = _summarize_race_day(d, df)
                    for ch in day_chunks:
                        ch["source_id"] = self.source.id
                        hashes.append(str(ch["content_hash"]))
                        chunks.append(ch)
                        items_new += 1
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
            content_hash="|".join(hashes[:40]) if hashes else None,
            metadata={
                "lookback_days": lookback_days,
                "max_days": max_days,
                "base_url": self.base,
            },
        )
        return run, chunks
