"""CLI for domain-brain knowledge ingestion.

Examples:
  python -m ingestion.cli --list
  python -m ingestion.cli --source tianxi-database
  python -m ingestion.cli --source tianxi-api
  python -m ingestion.cli --source tianxi-database --push-dify
  python -m ingestion.cli --health tianxi-database
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from connectors.tianxi_api import TianxiApiConnector
from connectors.tianxi_db import TianxiDbConnector
from ingestion.metrics import compute_health, write_health
from ingestion.models import SourceType
from ingestion.registry import find_source_by_id, load_sources_from_dir

ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = ROOT / "ingestion" / "sources"
RUNS_DIR = ROOT / "ingestion" / "runs"
CHUNKS_DIR = ROOT / "ingestion" / "chunks"
METRICS_DIR = ROOT / "ingestion" / "metrics"


def _maybe_push_dify(chunks: list, enabled: bool) -> None:
    if not enabled:
        return
    if not chunks:
        print("push-dify      : skipped (no chunks)")
        return
    try:
        from connectors.dify_push import push_chunks

        results = push_chunks(chunks, name_prefix="TianxiBrain")
        print(f"push-dify      : pushed {len(results)} document(s) → TianxiBrain")
    except Exception as e:  # noqa: BLE001
        print(f"push-dify      : FAILED — {e}")
        print("  Check DIFY_API_BASE / DIFY_API_KEY / DIFY_DATASET_ID")


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
    else:
        print(f"No connector implemented yet for type={source.type} id={source.id}")
        return 1

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    run_path = RUNS_DIR / f"{run.run_id}.json"
    run_path.write_text(run.model_dump_json(indent=2), encoding="utf-8")

    chunks_path = CHUNKS_DIR / f"{run.run_id}.json"
    chunks_path.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

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

    _maybe_push_dify(chunks, args.push_dify)
    return 0 if run.status.value in ("success", "partial") else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="domain-brain knowledge ingestion CLI")
    parser.add_argument("--list", action="store_true", help="List registered sources")
    parser.add_argument("--source", help="Source id to run")
    parser.add_argument("--health", help="Compute/print health metrics for a source id")
    parser.add_argument(
        "--sources-dir",
        type=Path,
        default=SOURCES_DIR,
        help="Directory containing source YAML files",
    )
    parser.add_argument("--lookback-days", type=int, default=10)
    parser.add_argument("--max-days", type=int, default=5)
    parser.add_argument(
        "--push-dify",
        action="store_true",
        help="After ingest, push chunks into Dify knowledge base (TianxiBrain)",
    )
    args = parser.parse_args(argv)

    sources = load_sources_from_dir(args.sources_dir)

    if args.list:
        if not sources:
            print("(no sources found)")
            return 0
        for s in sorted(sources, key=lambda x: (x.priority, x.id)):
            flag = "ON " if s.enabled else "OFF"
            print(f"[{flag}] p{s.priority}  {s.id:24}  {s.type.value:10}  {s.name}")
        return 0

    if args.health:
        metrics = compute_health(RUNS_DIR, args.health)
        path = write_health(metrics, METRICS_DIR)
        print(metrics.model_dump_json(indent=2))
        print(f"saved: {path}")
        return 0

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
