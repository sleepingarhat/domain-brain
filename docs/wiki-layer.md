# Wiki 編譯層

Chunk 唔會自己變聰明。Compile 把同一隻馬／騎師／場地嘅新來源 append 入已有頁。

## 目錄

```text
wiki/
  RULES.md
  index.md
  log.md
  entities/horses|jockeys|trainers|courses/
  concepts/
  sources/
  synthesis/          # 賽日，項目層
  style/              # 風格樣本，發佈人手批
```

## 頁契約

Frontmatter：`type id title aliases sources updated status layer`

章節：結論 → 觀察 → 矛盾 → 來源

觀察行格式：

```text
- YYYY-MM-DD · source_id · 賽果|預測 [[場地]] R? … · hash:xxxxxxxxxxxx
```

同 hash 唔重複寫。結論同矛盾只加唔刪。

## 點樣當記憶演化

1. 新 chunk 提到已有馬 → 只加觀察。
2. TX-Oracle 寫入 → 自動加「尚未用賽果核對」矛盾。
3. `write_reflection_to_wiki` → `wiki/synthesis/race-YYYY-MM-DD.md` + 相關馬頁 + 冷熱偏。
4. Mem0 可選，唔取代檔案。

## 唔做

- 唔為每一場開永久頁
- 唔改凍結預測
- 唔嗎 compile 刪舊結論
- 唔自動發社交
