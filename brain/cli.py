"""CLI for 天喜腦 local brain.

Examples:
  python -m brain.cli build
  python -m brain.cli query "7月15日跑馬地賽果"
  python -m brain.cli query "TX-Oracle 預測" --top-k 3
"""

from __future__ import annotations

import argparse

from brain.retrieve import build_index, search


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="天喜腦（TianxiBrain）本地檢索 CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("build", help="從 ingestion/chunks 重建索引")

    q = sub.add_parser("query", help="查詢知識")
    q.add_argument("text", help="查詢句子")
    q.add_argument("--top-k", type=int, default=5)

    args = parser.parse_args(argv)

    if args.cmd == "build":
        info = build_index()
        print(f"indexed {info['doc_count']} docs → {info['path']}")
        return 0 if info["doc_count"] else 1

    if args.cmd == "query":
        hits = search(args.text, top_k=args.top_k)
        if not hits:
            print("(no hits — 先跑 ingestion，再 python -m brain.cli build)")
            return 1
        for i, h in enumerate(hits, 1):
            print(f"\n===== #{i}  score={h.score}  source={h.source_id} =====")
            print(f"title: {h.title}")
            preview = h.content if len(h.content) < 1200 else h.content[:1200] + "\n…"
            print(preview)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
