---
type: prompt
purpose: "預測 vs 賽果寫入賽日 synthesis 同馬頁"
when: "完場之後；有綠燈完場樣本先跑實數"
writes: "wiki/synthesis/race-YYYY-MM-DD.md、相關 horse 頁、wiki/concepts/冷熱偏.md"
risk: append
inputs:
  - 完場賽果
  - 該日預測（只當觀察）
  - wiki/routing-map.md
---

## Prompt

Ground rules: 讀 `AGENTS.md`。禁止回測充場。無完場就停。

Job: reflection
1. 確認賽日已完場。缺賽果唔猜。
2. 用 `agents.reflection_agent.write_reflection_to_wiki`：開／追加 `wiki/synthesis/race-YYYY-MM-DD.md`，相關馬頁 append 觀察，冷熱偏 append 一行。
3. 預測同賽果並記。名單無重疊寫入矛盾，唔覆蓋結論。
4. 唔改凍結預測檔、唔改對外 hit-rate、唔發社交。
5. 摘要用人嘅語／賽果原文，唔評級。
