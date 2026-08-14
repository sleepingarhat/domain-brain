"""Simple CLI: domain-brain-run --source <id>"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from connectors.tianxi_db import TianxiDbConnector
from ingestion.models import SourceType
from ingestion.registry import find_source_by_id, load_sources_from_dir

ROOT = Path(__file__).resolve().parents[1]
SOURCES_DIR = ROOT / "ingestion" / "sources"
RUNS_DIR = ROOT / "ingestion" / "runs"
CHUNKS_DIR = ROOT / "ingestion" / "chunks"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a domain-brain knowledge source")
    parser.add_argument(
        "--source",
        required=True,
        help="Source id (e.g. tianxi-database)",
    )
    parser.add_argument(
        "--sources-dir",
        type=Path,
        default=SOURCES_DIR,
        help="Directory containing source YAML files",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=10,
        help="How many calendar days to look back for race results",
    )
    parser.add_argument(
        "--max-days",
        type=int,
        default=5,
        help="Max number of race-day CSVs to fetch",
    )
    args = parser.parse_args(argv)

    sources = load_sources_from_dir(args.sources_dir)
    source = find_source_by_id(sources, args.source)
    if source is None:
        print(f"Source not found: {args.source}")
        print("Available:", [s.id for s in sources])
        return 1
    if not source.enabled:
        print(f"Source is disabled: {source.id}")
        return 1

    if source.type == SourceType.DATABASE and source.id.startswith("tianxi"):
        connector = TianxiDbConnector(source)
        run, chunks = connector.run(
            lookback_days=args.lookback_days,
            max_days=args.max_days,
        )
    else:
        print(f"No connector implemented yet for type={source.type} id={source.id}")
        return 1

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    run_path = RUNS_DIR / f"{run.run_id}.json"
    run_path.write_text(
        run.model_dump_json(indent=2),
        encoding="utf-8",
    )

    chunks_path = CHUNKS_DIR / f"{run.run_id}.json"
    chunks_path.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"status        : {run.status.value}")
    print(f"items_fetched : {run.items_fetched}")
    print(f"items_new     : {run.items_new}")
    print(f"duration      : {run.duration_seconds}s")
    print(f"run saved     : {run_path}")
    print(f"chunks saved  : {chunks_path}")
    if run.error_message:
        print(f"error         : {run.error_message}")
    return 0 if run.status.value in ("success", "partial") else 1


if __name__ == "__init__":
    raise SystemExit(main())
