---
type: prompt
purpose: "Wiki 健康報告；lint 加矛盾／孤兒／死鏈"
when: "每月、dashboard 壞、合 PR 前"
writes: none
risk: read-only
inputs:
  - wiki/
  - eval/golden.json
  - AGENTS.md
---

## Prompt

Ground rules: 呢次 run 一字唔改。只出報告同建議動作。

Job: health
1. `python -m brain.cli lint`。列 issues。
2. 列 `wiki/` 孤兒頁（無來源、無觀察嘅實體）。
3. 掃最近矛盾；未用賽果核對嘅 TX-Oracle 觀察數一數。
4. 確認 `AGENTS.md`、`wiki/RULES.md`、`wiki/routing-map.md`、`wiki/hot.md` 存在。
5. `python -m brain.cli eval`，記 fail 題，唔改 golden。
6. 報告段落對 1–5，尾「建議下一步」每項係人要做或點名要你做。不自動修。
