"""CLI for domain-brain knowledge ingestion.

Examples:
  python -m ingestion.cli --list
  python -m ingestion.cli --source tianxi-database
  python -m ingestion.cli --feed-file notes/my-article.md --title "我的賽評"
  python -m ingestion.cli --feed-url https://idolhorse.com/some-article/
  python -m ingestion.cli --feed-dir ingestion/manual
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from connectors.tianxi_api import TianxiApiConnector
from connectors.tianxi_db import TianxiDbConnector
from connectors.web_static import WebStaticConnector
from ingestion.metrics import compute_health, write_health
from ingestion.models import CrawlRun, RunStatus, Source, SourceType
from ingestion.registry import find_source_by_id, load_sources_from_dir

ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = ROOT / "ingestion" / "sources"
RUNS_DIR = ROOT / "ingestion" / "runs"
CHUNKS_DIR = ROOT / "ingestion" / "chunks"
METRICS_DIR = ROOT / "ingestion" / "metrics"
MANUAL_DIR = ROOT / "ingestion" / "manual"
HK_TZ = timezone(timedelta(hours=8))


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _save_run_and_chunks(source_id: str, chunks: list[dict], status: RunStatus, error: str | None = None) -> int:
    started = datetime.now(HK_TZ)
    run_id = f"{started.strftime('%Y%m%d-%H%M%S')}-{source_id}"
    finished = datetime.now(HK_TZ)
    run = CrawlRun(
        run_id=run_id,
        source_id=source_id,
        started_at=started,
        finished_at=finished,
        status=status,
        items_fetched=len(chunks),
        items_new=len(chunks),
        error_message=error,
        duration_seconds=round((finished - started).total_seconds(), 2),
    )
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    run_path = RUNS_DIR / f"{run.run_id}.json"
    run_path.write_text(run.model_dump_json(indent=2), encoding="utf-8")
    chunks_path = CHUNKS_DIR / f"{run.run_id}.json"
    chunks_path.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    health = compute_health(RUNS_DIR, source_id)
    health_path = write_health(health, METRICS_DIR)
    print(f"status        : {run.status.value}")
    print(f"items_new     : {run.items_new}")
    print(f"run saved     : {run_path}")
    print(f"chunks saved  : {chunks_path}")
    print(f"health saved  : {health_path}")
    if error:
        print(f"error         : {error}")
    print("下一步: python -m brain.cli build")
    return 0 if status in (RunStatus.SUCCESS, RunStatus.PARTIAL) else 1


def _feed_text(title: str, content: str, source_id: str = "manual", meta: dict | None = None) -> list[dict]:
    body = content.strip()
    if not body:
        return []
    return [
        {
            "source_id": source_id,
            "title": title or "manual-note",
            "content": body[:20000],
            "content_hash": _hash(body),
            "metadata": meta or {"kind": "manual"},
        }
    ]


def _run_source(source, args) -> int:
    if source.type == SourceType.DATABASE and "tianxi" in source.id:
        connector = TianxiDbConnector(source)
        run, chunks = connector.run(
            lookback_days=args.lookback_days,
            max_days=args.max_days,
        )
    elif source.type == SourceType.API and "tianxi" in source.id:
        connector = TianxiApiConnector(source)
        run, chunks = connector.run()
    elif source.type == SourceType.WEB_CRAWL:
        connector = WebStaticConnector(source)
        run, chunks = connector.run()
    else:
        print(f"No connector implemented yet for type={source.type} id={source.id}")
        return 1

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    run_path = RUNS_DIR / f"{run.run_id}.json"
    run_path.write_text(run.model_dump_json(indent=2), encoding="utf-8")
    chunks_path = CHUNKS_DIR / f"{run.run_id}.json"
    chunks_path.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    health = compute_health(RUNS_DIR, source.id)
    health_path = write_health(health, METRICS_DIR)
    print(f"status        : {run.status.value}")
    print(f"items_fetched : {run.items_fetched}")
    print(f"items_new     : {run.items_new}")
    print(f"duration      : {run.duration_seconds}s")
    print(f"run saved     : {run_path}")
    print(f"chunks saved  : {chunks_path}")
    print(f"health saved  : {health_path}")
    if run.error_message:
        print(f"error         : {run.error_message}")
    print("下一步: python -m brain.cli build")
    return 0 if run.status.value in ("success", "partial") else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="domain-brain knowledge ingestion CLI")
    parser.add_argument("--list", action="store_true", help="List registered sources")
    parser.add_argument("--source", help="Source id to run")
    parser.add_argument("--health", help="Compute/print health metrics for a source id")
    parser.add_argument("--sources-dir", type=Path, default=SOURCES_DIR)
    parser.add_argument("--lookback-days", type=int, default=10)
    parser.add_argument("--max-days", type=int, default=5)

    # Manual feed
    parser.add_argument("--feed-file", type=Path, help="餵入一個本地 .md/.txt 檔")
    parser.add_argument("--feed-url", help="餵入一個公開文章 URL（靜態抓取）")
    parser.add_argument("--feed-dir", type=Path, help="餵入資料夾內全部 .md/.txt")
    parser.add_argument("--title", help="人手餵入時的標題")

    args = parser.parse_args(argv)
    sources = load_sources_from_dir(args.sources_dir)

    if args.list:
        if not sources:
            print("(no sources found)")
            return 0
        for s in sorted(sources, key=lambda x: (x.priority, x.id)):
            flag = "ON " if s.enabled else "OFF"
            print(f"[{flag}] p{s.priority}  {s.id:28}  {s.type.value:10}  {s.name}")
        return 0

    if args.health:
        metrics = compute_health(RUNS_DIR, args.health)
        path = write_health(metrics, METRICS_DIR)
        print(metrics.model_dump_json(indent=2))
        print(f"saved: {path}")
        return 0

    # --- manual feeds ---
    if args.feed_file:
        path = args.feed_file
        if not path.exists():
            print(f"檔案不存在: {path}")
            return 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        title = args.title or path.stem
        chunks = _feed_text(title, text, meta={"kind": "manual", "path": str(path)})
        return _save_run_and_chunks("manual", chunks, RunStatus.SUCCESS if chunks else RunStatus.FAILED, None if chunks else "empty file")

    if args.feed_dir:
        d = args.feed_dir
        if not d.exists():
            print(f"資料夾不存在: {d}")
            return 1
        chunks: list[dict] = []
        for path in sorted(list(d.glob("*.md")) + list(d.glob("*.txt"))):
            text = path.read_text(encoding="utf-8", errors="ignore")
            chunks.extend(_feed_text(path.stem, text, meta={"kind": "manual", "path": str(path)}))
        return _save_run_and_chunks("manual", chunks, RunStatus.SUCCESS if chunks else RunStatus.FAILED, None if chunks else "no md/txt files")

    if args.feed_url:
        pseudo = Source(
            id="manual-url",
            name=args.title or args.feed_url,
            type=SourceType.WEB_CRAWL,
            enabled=True,
            url=args.feed_url,
            config={"seed_urls": [args.feed_url], "delay_seconds": 0.5},
        )
        conn = WebStaticConnector(pseudo)
        run, chunks = conn.run()
        for ch in chunks:
            ch["source_id"] = "manual"
        return _save_run_and_chunks(
            "manual",
            chunks,
            run.status,
            run.error_message,
        )

    if not args.source:
        parser.print_help()
        return 1

    source = find_source_by_id(sources, args.source)
    if source is None:
        print(f"Source not found: {args.source}")
        print("Available:", [s.id for s in sources])
        return 1
    if not source.enabled:
        print(f"Source is disabled: {source.id}")
        return 1

    return _run_source(source, args)


if __name__ == "__main__":
    raise SystemExit(main())
