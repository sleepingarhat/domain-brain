#!/usr/bin/env bash
# Incremental style/knowledge refresh for this box (PUBLIC repo safe).
# Suggested cron (HKT): race mornings 08:30 + next-day 01:00 + weekly Mon 12:00 for YouTube
#   30 8 * * 0,3   /workspace/domain-brain/scripts/style_refresh.sh
#   0 1 * * 1,4    /workspace/domain-brain/scripts/style_refresh.sh
#   0 12 * * 1     /workspace/domain-brain/scripts/style_refresh.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p logs
LOG="logs/refresh_$(TZ=Asia/Hong_Kong date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1

echo "=== style_refresh $(date -Is) ==="
# read-only pull of code; never push from cron
git pull --ff-only origin feature/style-exemplars 2>/dev/null || git pull --ff-only origin main || true

if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
else
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install -e ".[style,dev]"
fi

python scripts/crawl_style_sources.py
python -m brain.cli build || true
# style-build from private full chunks is already done inside crawl; rebuild profiles if needed
python -m brain.cli style --situation 大熱門 --k 2 || true
echo "=== done $(date -Is) log=$LOG ==="
