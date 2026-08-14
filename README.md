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
    CrewAI Agents     TX-Oracle      Style / Content
    (反思 / 分析)     (預測引擎)      (風格克隆產出)
```

### 為什麼自建 Source Registry？

目前頂級工具（Firecrawl ~160k★、Crawl4AI ~76k★、Dify Knowledge Pipeline）在「爬取」與「入庫」已經很強，但**來源級清晰列表 + 完整爬取記錄 + 有效性／穩定性指標 + 選擇性增刪啟停**仍然是大多數系統的缺口。  
這層做成一級公民，直接對應未來產品前端的「知識來源管理」頁面，是產品差異化的關鍵。

---

## Knowledge Ingestion Layer（核心設計）

支援四種餵入方式，全部由同一套 **Source Registry** 管理：

| 類型 | 說明 | MVP 優先 |
|------|------|----------|
| `database` | 直接接駁 `tianxi-database` CSV / `tianxi-backend` API | 最高 |
| `api` | 外部 API（新聞、其他預測、自有服務） | 高 |
| `web_crawl` | 定期自動爬取指定網站（Crawl4AI / Firecrawl） | 高 |
| `rss` | RSS / Atom 訂閱 | 中 |
| `manual` | 人手上傳文件 / 貼文 / 風格樣本 | 高 |

每個來源都有：
- 清晰設定（啟停、頻率、標籤、優先級）
- 每次執行的 **Crawl Run** 記錄
- 聚合 **Health Metrics**（成功率、新鮮度、連續失敗次數等）

詳見 → [`docs/knowledge-ingestion.md`](docs/knowledge-ingestion.md)  
Schema → [`schemas/source-registry.schema.json`](schemas/source-registry.schema.json)

---

## 技術棧（MVP）

| 層級 | 選擇 | 備註 |
|------|------|------|
| 結構化賽馬數據 | tianxi-database + tianxi-backend | 已有生產級管道，直接接駁 |
| Web 爬取引擎 | Crawl4AI（自托管優先）或 Firecrawl | 2026 頂級 LLM-ready crawler |
| 知識庫 / RAG | Dify（Knowledge Pipeline） | 視覺化 + API |
| 長期記憶 | Mem0 | 記憶演化核心 |
| 多 Agent | CrewAI | 反思、內容、分析角色 |
| 調度 | GitHub Actions / Cloudflare Cron | 與 tianxi 同一風格 |

---

## 資料夾結構（規劃）

```
domain-brain/
├── README.md
├── docs/
│   ├── knowledge-ingestion.md      # 本層完整設計
│   └── architecture.md             # 整體架構（後續）
├── schemas/
│   ├── source-registry.schema.json
│   └── crawl-run.schema.json
├── ingestion/
│   ├── sources/                    # 來源定義（YAML/JSON）
│   ├── runs/                       # 執行記錄
│   └── metrics/                    # 健康指標聚合
├── connectors/                     # 各類型連接器實作
│   ├── tianxi_db.py
│   ├── tianxi_api.py
│   ├── web_crawl4ai.py
│   └── manual.py
└── examples/
    └── sources/
        └── tianxi-database.example.yaml
```

---

## 市場定位（簡述）

- **不是**「再多一個通用爬蟲 / RAG 框架」
- **而是**「可運營、有記憶、有數據護城河的垂直領域大腦」
- 第一垂直：**香港賽馬（馬神）**
- 後續可快速遷移至其他領域（玄學、足球等）
- 知識來源管理層做成產品級功能，是主要差異化點之一

---

## 當前狀態

- [x] 架構與 Knowledge Ingestion 設計落地
- [ ] Source Registry Schema + 示例來源
- [ ] tianxi-database / tianxi-backend connector
- [ ] 基礎 Crawl Run + Health Metrics 記錄
- [ ] Dify + Mem0 接駁骨架
- [ ] 第一個 CrewAI Reflection Agent

---

## License

MIT
