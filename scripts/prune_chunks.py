"""Drop ingestion chunk files older than keep-days (by filename prefix YYYYMMDD)."""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "ingestion" / "chunks"
HK = timezone(timedelta(hours=8))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--keep-days", type=int, default=21)
    args = p.parse_args()
    if not CHUNKS.exists():
        return 0
    cutoff = datetime.now(HK) - timedelta(days=args.keep_days)
    removed = 0
    for path in CHUNKS.glob("*.json"):
        stamp = path.name[:8]
        if not stamp.isdigit():
            continue
        try:
            created = datetime.strptime(stamp, "%Y%m%d").replace(tzinfo=HK)
        except ValueError:
            continue
        if created < cutoff:
            path.unlink()
            removed += 1
            print(f"removed {path.name}")
    print(f"removed={removed} keep_days={args.keep_days}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
