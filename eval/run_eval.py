"""CLI wrapper: python -m eval.run_eval  (also: python -m brain.cli eval)."""

from brain.eval_golden import run

if __name__ == "__main__":
    import json

    report = run()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report.get("skipped"):
        raise SystemExit(0)
    raise SystemExit(1 if report.get("failed") else 0)
