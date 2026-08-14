# domain-brain

**可產品化的領域 AI 大腦**  
記憶演化 · 風格克隆 · 知識餵入 · 社交媒體半自動運營

> MVP 目標：**馬神（Horse God）** — 以香港賽馬為第一領域，結合 `tianxi-database` + `tianxi-backend`（TX-Oracle）的高質量數據與預測能力。

---

## 核心能力

| 能力 | 說明 |
|------|------|
| **記憶演化** | Mem0 長期記憶 + 賽後反思閉環（預測 vs 實績 → 策略更新） |
| **風格克隆** | 從 ebook / blogger / 既有文案學習寫作風格，用於內容生成 |
| **知識餵入** | 統一 Knowledge Ingestion Layer（人手、API、數據庫、定期爬取） |
| **半自動運營** | 社交媒體（先 Weibo）內容生成與排程 |

---

## 架構總覽

```
┌─────────────────────────────────────────────────────────────┐
│                    Knowledge Ingestion Layer                 │
│  Source Registry  ·  Crawl Runs  ·  Health Metrics          │
│  (web / rss / api / database / manual)                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Dify Knowledge Base  +  Mem0 Memory Layer                   │
│  (RAG + 長期記憶演化)                                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    Reflection Agent  TX-Oracle      Style / Content
    (賽後反思)         (預測引擎)      (風格克隆產出)
```

---

## Quick Start

```bash
pip install -e .

# 列出已註冊來源
python -m ingestion.cli --list

# 跑結構化賽果（tianxi-database）
python -m ingestion.cli --source tianxi-database --lookback-days 14 --max-days 5

# 跑預測 API（需先改 ingestion/sources/tianxi-api.yaml 的 base_url）
python -m ingestion.cli --source tianxi-api

# 查看健康指標
python -m ingestion.cli --health tianxi-database
```

輸出：
- `ingestion/runs/<run_id>.json` — Crawl Run
- `ingestion/chunks/<run_id>.json` — 知識片段
- `ingestion/metrics/<source_id>.json` — Health Metrics

---

## 已實作組件

| 組件 | 路徑 | 狀態 |
|------|------|------|
| Source Registry + Schema | `schemas/`, `ingestion/sources/` | ✅ |
| Crawl Run 記錄 | `ingestion/runs/` | ✅ |
| Health Metrics 聚合 | `ingestion/metrics.py` | ✅ |
| tianxi-database connector | `connectors/tianxi_db.py` | ✅ 可跑 |
| tianxi-backend API connector | `connectors/tianxi_api.py` | ✅（需填 base_url） |
| Dify push skeleton | `connectors/dify_push.py` | ✅ |
| Reflection Agent skeleton | `agents/reflection_agent.py` | ✅ |
| 排程 GHA | `.github/workflows/ingest-tianxi.yml` | ✅ |
| web_crawl (Crawl4AI) | — | 🔜 下一階段 |
| Mem0 正式寫入 | — | 🔜 接 key 後啟用 |
| 完整 CrewAI multi-agent | — | 🔜 |

---

## 技術棧（MVP）

| 層級 | 選擇 |
|------|------|
| 結構化數據 | tianxi-database + tianxi-backend |
| Web 爬蟲（規劃） | Crawl4AI / Firecrawl |
| 知識庫 | Dify Knowledge API |
| 長期記憶 | Mem0 |
| Agent | Reflection skeleton → CrewAI |
| 調度 | GitHub Actions |

---

## 資料夾結構

```
domain-brain/
├── README.md
├── pyproject.toml
├── docs/knowledge-ingestion.md
├── schemas/
├── ingestion/
│   ├── models.py / registry.py / metrics.py / cli.py
│   ├── sources/          # 來源 YAML（可增刪啟停）
│   ├── runs/ chunks/ metrics/
├── connectors/
│   ├── tianxi_db.py
│   ├── tianxi_api.py
│   └── dify_push.py
├── agents/
│   └── reflection_agent.py
└── .github/workflows/ingest-tianxi.yml
```

---

## 市場定位

- 不是再多一個通用爬蟲 / RAG 框架
- 而是**可運營、有記憶、有數據護城河的垂直領域大腦**
- 第一垂直：香港賽馬（馬神）
- 知識來源管理層（清晰列表 + 健康指標 + 選擇性增刪）是產品差異化重點

---

## License

MIT
