"""Aggregate Health Metrics from stored Crawl Run JSON files."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from ingestion.models import CrawlRun, HealthMetrics, RunStatus

HK_TZ = timezone(timedelta(hours=8))


def _parse_runs(runs_dir: Path, source_id: str | None = None) -> list[CrawlRun]:
    if not runs_dir.exists():
        return []
    runs: list[CrawlRun] = []
    for path in sorted(runs_dir.glob("*.json")):
        try:
            run = CrawlRun.model_validate_json(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if source_id is None or run.source_id == source_id:
            runs.append(run)
    return runs


def compute_health(
    runs_dir: Path,
    source_id: str,
    now: datetime | None = None,
) -> HealthMetrics:
    """Compute health metrics for one source from its recent runs."""
    now = now or datetime.now(HK_TZ)
    runs = _parse_runs(runs_dir, source_id=source_id)
    runs.sort(key=lambda r: r.started_at, reverse=True)

    def _rate(window_days: int) -> float | None:
        cutoff = now - timedelta(days=window_days)
        window = [r for r in runs if r.started_at >= cutoff]
        if not window:
            return None
        ok = sum(1 for r in window if r.status in (RunStatus.SUCCESS, RunStatus.PARTIAL))
        return round(ok / len(window), 4)

    consecutive_failures = 0
    for r in runs:
        if r.status == RunStatus.FAILED:
            consecutive_failures += 1
        else:
            break

    last_success_at = next(
        (r.finished_at or r.started_at for r in runs if r.status == RunStatus.SUCCESS),
        None,
    )
    last_run_at = runs[0].started_at if runs else None

    recent = runs[:20]
    avg_items_new = (
        round(sum(r.items_new for r in recent) / len(recent), 2) if recent else None
    )
    durations = [r.duration_seconds for r in recent if r.duration_seconds is not None]
    avg_duration = round(sum(durations) / len(durations), 2) if durations else None

    return HealthMetrics(
        source_id=source_id,
        success_rate_7d=_rate(7),
        success_rate_30d=_rate(30),
        consecutive_failures=consecutive_failures,
        last_success_at=last_success_at,
        last_run_at=last_run_at,
        avg_items_new=avg_items_new,
        avg_duration_seconds=avg_duration,
        updated_at=now,
    )


def write_health(metrics: HealthMetrics, metrics_dir: Path) -> Path:
    metrics_dir.mkdir(parents=True, exist_ok=True)
    path = metrics_dir / f"{metrics.source_id}.json"
    path.write_text(metrics.model_dump_json(indent=2), encoding="utf-8")
    return path
