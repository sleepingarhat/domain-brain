"""CLI for 天喜腦 local brain.

Examples:
  python -m brain.cli build
  python -m brain.cli query "7月15日跑馬地賽果"
  python -m brain.cli query "架勢奇爸" --top-k 3 --answer
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
    q.add_argument(
        "--answer",
        action="store_true",
        help="若已設 OPENAI_API_KEY，用檢索結果生成精簡答覆",
    )

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

        if args.answer:
            try:
                from brain.answer import synthesize_answer

                ans = synthesize_answer(args.text, hits)
            except Exception as e:  # noqa: BLE001
                print(f"[answer error] {e}")
                ans = None
            if ans:
                print("===== 天喜腦答覆 =====")
                print(ans)
                print()
            else:
                print(
                    "(未生成答覆：請設定 OPENAI_API_KEY；"
                    "可選 OPENAI_BASE_URL / OPENAI_MODEL)\n"
                )

        for i, h in enumerate(hits, 1):
            print(f"\n===== #{i}  score={h.score}  source={h.source_id} =====")
            print(f"title: {h.title}")
            preview = h.content if len(h.content) < 1200 else h.content[:1200] + "\n…"
            print(preview)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
