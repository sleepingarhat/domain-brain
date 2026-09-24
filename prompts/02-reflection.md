---
type: prompt
purpose: "預測 vs 賽果寫入賽日 synthesis 同馬頁"
when: "完場之後；有綠燈完場樣本先跑實數"
writes: "wiki/synthesis/race-YYYY-MM-DD.md、相關 horse 頁、wiki/concepts/冷熱偏.md"
risk: append
inputs:
  - tianxi-database 完場 chunks
  - 同日 tianxi-api chunks（可選，只當觀察）
  - wiki/routing-map.md
---

## Prompt

Ground rules: 讀 `AGENTS.md`。禁止回測充場。無完場就停。

Job: reflection
1. 綠燈：該日有 `tianxi-database` 單場賽果，並有名次馬。未來日、只有 today-picks、只有 hit-rate 都唔算。
2. 跑 `python -m brain.cli reflect` （視窗內最近 1–2 個完場日）或 `python -m brain.cli reflect --date YYYY-MM-DD`。
3. 預測樣本可缺；缺就在矛盾欄記「未回測充場」，唔用歷史預測填。
4. 只 append `wiki/synthesis/` 同相關馬頁。唔改凍結預測、唔改對外 hit-rate、唔發社交。
5. 摘要用賽果原文名單，唔評級。
