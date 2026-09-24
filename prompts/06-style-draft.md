---
type: prompt
purpose: "用已有 wiki 觀察草撰社交，先學聲線"
when: "人點名要草稿；未開自動發佈"
writes: "wiki/style/ 草稿頁"
risk: append
inputs:
  - wiki/style/ 已刊樣本
  - 相關 entities / synthesis
---

## Prompt

Ground rules: 發佈一定人手批。唔發明統計。缺證據標 `[needs source]`。

Job: style-draft
1. 數 `wiki/style/` 內 `status: sample` 頁。不足兩篇就停，叫人先跑 `python -m brain.cli style-seed --file ...`。唔好用通用 AI 口吻頂替。
2. 讀最多三篇樣本。用兩句講聲線，等人精正先草。
3. 只用 wiki 結論／觀察／賽日 synthesis 做材料。凍結預測唔引當已完場事實。
4. 草稿寫入 `wiki/style/` 新檔。`status: draft`。
5. 唔呼發佈 API。結束列出來源頁，等人批發。
