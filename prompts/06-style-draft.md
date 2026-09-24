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
1. 讀 `wiki/style/` 最多三篇已有樣本。用兩句講聲線（句長、第一／二人稱、點題方式），等人精正先草。
2. 只用 wiki 結論／觀察／賽日 synthesis 做材料。凍結預測唔引當已完場事實。
3. 草稿寫入 `wiki/style/` 新檔或追加段落。`status: draft`。
4. 唔移出 `wiki/style/`、唔呼發佈 API、唔改實體結論。
5. 結束列出用過邊些來源頁，等人批發。
