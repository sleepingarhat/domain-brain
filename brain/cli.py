"""CLI for 天喜腦 local brain.

Examples:
  python -m brain.cli compile
  python -m brain.cli build
  python -m brain.cli lint
  python -m brain.cli eval
  python -m brain.cli reflect
  python -m brain.cli reflect --date 2026-09-21
  python -m brain.cli query "7月15日跑馬地賽果"
  python -m brain.cli query "架勢奇爸" --layer wiki --top-k 3
"""

from __future__ import annotations

import argparse
import json

from brain.retrieve import build_index, search


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="天喜腦（TianxiBrain）本地檢索 CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("compile", help="由 chunks 編譯／更新 wiki 實體頁（只 append）")
    sub.add_parser("build", help="從 chunks + wiki 重建 BM25 索引")
    sub.add_parser("lint", help="檢查 wiki 頁契約（唯讀）")
    ev = sub.add_parser("eval", help="跑 eval/golden.json")
    ev.add_argument("--strict", action="store_true")

    rf = sub.add_parser("reflect", help="完場綠燈賽日：預測 vs 賽果 append 入 wiki")
    rf.add_argument("--date", help="YYYY-MM-DD；缺席則取視窗內最近綠燈日")
    rf.add_argument("--lookback-days", type=int, default=5)
    rf.add_argument("--max-days", type=int, default=2, help="一次最多幾個完場日（禁回測充場）")
    rf.add_argument("--model-version", default="tx-oracle-observation")

    q = sub.add_parser("query", help="查詢知識")
    q.add_argument("text", help="查詢句子")
    q.add_argument("--top-k", type=int, default=5)
    q.add_argument(
        "--layer",
        choices=("all", "wiki", "chunks"),
        default="all",
        help="all=混合；wiki=只實體頁；chunks=只原文",
    )
    q.add_argument(
        "--answer",
        action="store_true",
        help="若已設 OPENAI_API_KEY，用檢索結果生成精簡答覆",
    )

    args = parser.parse_args(argv)

    if args.cmd == "compile":
        from brain.compile import compile_chunks

        info = compile_chunks()
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 0 if info["chunks"] or info["observations"] else 1

    if args.cmd == "build":
        info = build_index()
        print(
            f"indexed {info['doc_count']} docs "
            f"(chunks={info.get('chunk_count')} wiki={info.get('wiki_count')}) "
            f"→ {info['path']}"
        )
        return 0 if info["doc_count"] else 1

    if args.cmd == "lint":
        from brain.lint_wiki import lint_wiki

        report = lint_wiki()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report.get("ok") else 1

    if args.cmd == "eval":
        from brain.eval_golden import run

        report = run()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if report.get("skipped"):
            return 1 if args.strict else 0
        return 1 if report.get("failed") else 0

    if args.cmd == "reflect":
        from agents.reflect_run import reflect_completed

        report = reflect_completed(
            date=args.date,
            lookback_days=args.lookback_days,
            max_days=args.max_days,
            model_version=args.model_version,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if args.date and report.get("reason") == "no_green_results":
            return 2
        return 0 if report.get("ok") else 1

    if args.cmd == "query":
        hits = search(args.text, top_k=args.top_k, layer=args.layer)
        if not hits:
            print(（no hits — 先跑 ingestion，再 python -m brain.cli compile && python -m brain.cli build）")
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
                    "（未生成答覆：請設定 OPENAI_API_KEY；"
                    "可選 OPENAI_BASE_URL / OPENAI_MODEL）\n"
                )

        for i, h in enumerate(hits, 1):
            kind = (h.metadata or {}).get("kind") or "chunk"
            print(f"\n===== #{i}  score={h.score}  source={h.source_id}  layer={kind} =====")
            print(f"title: {h.title}")
            preview = h.content if len(h.content) < 1200 else h.content[:1200] + "\n…"
            print(preview)
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
