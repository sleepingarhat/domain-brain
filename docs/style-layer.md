# 風格層

社交草稿要先有你認得出係天喜嘅已刊短文。倉內不生產範本聲線。

## 塞樣本

每篇至少四十字，建議 2–3 篇不同場次。

```bash
python -m brain.cli style-seed --file notes/posted-1.md --title "谷評-2026-09"
python -m brain.cli style-seed --file notes/posted-2.md --title "田評-2026-09"
```

寫入 `wiki/style/<title>.md`，`status: sample`。唔發佈。

## 草稿

讀 `prompts/06-style-draft.md`。樣本不足三篇時卡要停，唔好用通用 AI 口吻頂替。
草稿只入 `wiki/style/`，`status: draft`。出街一定人手批。
