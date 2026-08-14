# 天喜腦（TianxiBrain）本地檢索 — 方案 B

免費、可在本機或 CI 跑通。不依賴雲端知識庫付費額度。

---

## 流程

```text
tianxi-database / tianxi-api
        ↓
python -m ingestion.cli --source …
        ↓
ingestion/chunks/*.json
        ↓
python -m brain.cli build
        ↓
brain/index/corpus.json
        ↓
python -m brain.cli query "你的問題"
```

---

## 指令

```bash
pip install -e .

python -m ingestion.cli --source tianxi-database --lookback-days 40 --max-days 5
python -m ingestion.cli --source tianxi-api

python -m brain.cli build
python -m brain.cli query "7月15日跑馬地"
python -m brain.cli query "TX-Oracle 預測" --top-k 3
```

亦可用 entry point：`tianxi-brain build` / `tianxi-brain query "…"`

---

## 特點

| 項目 | 說明 |
|------|------|
| 費用 | 無 embedding／雲端知識庫 credits |
| 算法 | BM25 + 中英簡易分詞（含 CJK bigram） |
| 資料 | tianxi 既有管線 |
| 日後升級 | 可換成向量／混合檢索，而不改 ingestion 契約 |

---

## 注意

- 索引目錄 `brain/index/` 預設 gitignore，每次 ingest 後記得 `build`
- 查詢無命中時：先確認已跑 ingestion 且 `build` 成功
