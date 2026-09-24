---
type: prompt
purpose: "跑黃金問題，抓回歸退步"
when: "compile/build 後；改 retrieve 前"
writes: none
risk: read-only
inputs:
  - eval/golden.json
  - BM25 index + wiki
---

## Prompt

Ground rules: 唔改 `eval/golden.json`。Fail 就報，唔改題契來讓它 pass。

Job: eval
1. `python -m brain.cli eval`。
2. 列 fail 題、命中層、缺頁。
3. 若要加題，出完整 JSON 草稿等批，不直接寫入。
4. 唔用回測充場當正例。
