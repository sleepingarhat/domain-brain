# 天喜腦（TianxiBrain）本地開源檢索 — 方案 B

**不依賴 Dify Cloud AI Credits。**  
知識仍由 `ingestion` 餵入；檢索用純 Python BM25，可喺本機或 GitHub Actions 跑。

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

# 1. 拉知識
python -m ingestion.cli --source tianxi-database --lookback-days 40 --max-days 5
python -m ingestion.cli --source tianxi-api

# 2. 建索引
python -m brain.cli build
# 或: tianxi-brain build

# 3. 查詢
python -m brain.cli query "7月15日跑馬地"
python -m brain.cli query "TX-Oracle 預測 架勢" --top-k 3
```

---

## 特點

| 項目 | 說明 |
|------|------|
| 依賴 | 無 embedding API、無 Dify credits |
| 算法 | BM25 + 中英簡易分詞（含 CJK bigram） |
| 資料 | 全部嚟自你已有嘅 tianxi 管線 |
| 擴展 | 之後可加本地 embedding / 接 LLM 做摘要答案 |

---

## 同 Dify 關係

- Dify Cloud：**可選**，不再係必需
- 若將來有主機，仍可並行推去開源 Dify
- 而家產品核心檢索以本模組為準
