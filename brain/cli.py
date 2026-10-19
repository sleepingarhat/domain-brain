"""CLI for 天喜腦 local brain.

Examples:
  python -m brain.cli compile
  python -m brain.cli build
  python -m brain.cli lint
  python -m brain.cli eval
  python -m brain.cli reflect
  python -m brain.cli reflect --date 2026-09-21
  python -m brain.cli query "7月15日跑馬地賽果"
  python -m brain.cli style-build
  python -m brain.cli style --situation 大熱門 --k 5
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


    sb = sub.add_parser("style-build", help="由 style chunks 編譯 exemplars + 統計風格檔案")
    sb.add_argument("--no-profiles", action="store_true", help="唔寫 wiki/style/profiles")

    st = sub.add_parser("style", help="檢索風格 exemplar 段落")
    st.add_argument("--situation", default=None, help="大熱門／混戰／冷馬有價／新馬或初出／距離或場地轉變／其他")
    st.add_argument("--commentator", default=None, help="source id 或 commentator id")
    st.add_argument("--query", default=None, help="額外關鍵詞（可選）")
    st.add_argument("--k", type=int, default=5)
    st.add_argument(
        "--from-frozen",
        type=str,
        default=None,
        help="凍結 JSON 路徑；配合 --race 自動判斷 situation",
    )
    st.add_argument("--race", type=int, default=None, help="場次（配合 --from-frozen）")

    sc = sub.add_parser("style-check", help="檢查草稿有冇 verbatim 抄 exemplar（≥12 字）")
    sc.add_argument("--text", required=True, help="待檢查嘅評述正文")
    sc.add_argument("--situation", default=None)
    sc.add_argument("--commentator", default=None)
    sc.add_argument("--k", type=int, default=20, help="對照最近檢索到嘅 exemplars 數量")
    sc.add_argument("--min-chars", type=int, default=12)

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
            f"-> {info['path']}"
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
            print("(no hits - run ingestion, then python -m brain.cli compile && python -m brain.cli build)")
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
            kind = (h.metadata or {}).get("kind") or "chunk"
            print(f"\n===== #{i}  score={h.score}  source={h.source_id}  layer={kind} =====")
            print(f"title: {h.title}")
            preview = h.content if len(h.content) < 1200 else h.content[:1200] + "\n..."
            print(preview)
        return 0

    if args.cmd == "style-build":
        from brain.style import build_exemplars

        info = build_exemplars(write_profiles=not args.no_profiles)
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 0 if info.get("exemplar_count") else 1

    if args.cmd == "style":
        from brain.style import classify_race_from_frozen, retrieve_exemplars

        situation = args.situation
        if args.from_frozen and args.race is not None:
            situation = classify_race_from_frozen(args.from_frozen, args.race)
            print(f"[situation] {situation}  (from {args.from_frozen} race {args.race})")
        hits = retrieve_exemplars(
            situation=situation,
            commentator=args.commentator,
            query=args.query or situation,
            k=args.k,
        )
        if not hits:
            print("(no style exemplars — crawl style sources, then python -m brain.cli style-build)")
            return 1
        for i, h in enumerate(hits, 1):
            print(f"\n===== #{i}  score={h.score}  situation={h.situation}  commentator={h.commentator} =====")
            print(f"id: {h.id}")
            if h.url:
                print(f"url: {h.url}")
            print(h.text if len(h.text) < 800 else h.text[:800] + "\n...")
        return 0

    if args.cmd == "style-check":
        from brain.style import reject_if_verbatim, retrieve_exemplars

        exemplars = retrieve_exemplars(
            situation=args.situation,
            commentator=args.commentator,
            query=args.situation,
            k=args.k,
        )
        ok, hits = reject_if_verbatim(args.text, exemplars, min_chars=args.min_chars)
        print(json.dumps({"ok": ok, "hits": hits}, ensure_ascii=False, indent=2))
        return 0 if ok else 2


    return 1


if __name__ == "__main__":
    raise SystemExit(main())
