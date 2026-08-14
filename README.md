# domain-brain · 天喜腦（TianxiBrain）

**可產品化的領域 AI 大腦（免費本地路徑）**  
知識餵入 · 來源管理 · 本地檢索 · 可擴展記憶／風格／運營

> 產品名：**天喜腦（TianxiBrain）**  
> 第一領域：香港賽馬（`tianxi-database` + `tianxi-backend` / TX-Oracle）  
> **現行路線：方案 B** — 全流程可在本機 / GitHub 免費跑通，**不依賴任何雲端知識庫付費額度**。

---

## 30 秒跑通

```bash
git clone https://github.com/sleepingarhat/domain-brain.git
cd domain-brain
pip install -e .

# 1) 餵知識
python -m ingestion.cli --list
python -m ingestion.cli --source tianxi-database --lookback-days 40 --max-days 5
python -m ingestion.cli --source tianxi-api

# 2) 建本地索引
python -m brain.cli build

# 3) 查詢天喜腦
python -m brain.cli query "7月15日跑馬地"
python -m brain.cli query "架勢奇爸" --top-k 3
```

詳細說明：[docs/brain-local.md](docs/brain-local.md) · [docs/knowledge-ingestion.md](docs/knowledge-ingestion.md)

---

## 架構（方案 B）

```text
┌──────────────────────────────────────────────┐
│           Knowledge Ingestion Layer            │
│  Source Registry · Crawl Runs · Health Metrics │
│  types: database / api / web / rss / manual    │
└─────────────────────┬────────────────────────┘
                      │ chunks/
                      ▼
┌──────────────────────────────────────────────┐
│         天喜腦本地檢索（brain/）                │
│         純 Python BM25 · 零 embedding 費用      │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
              brain.cli query

之後可選（未接為必需）：Mem0 長期記憶、本地 embedding、LLM 摘要回答
```

---

## 核心能力

| 能力 | 現狀 |
|------|------|
| **知識餵入** | ✅ Source Registry + CLI + Run 記錄 + Health |
| **tianxi 數據** | ✅ database CSV + TX-Oracle API |
| **本地檢索** | ✅ BM25（`brain/`） |
| **來源可增刪啟停** | ✅ YAML registry（前端可對應） |
| **長期記憶** | 骨架（`connectors/mem0_push.py`，可選） |
| **賽後反思 Agent** | 骨架（`agents/reflection_agent.py`） |
| **風格克隆 / 社媒** | 規劃中 |
| **Web 爬蟲** | 規劃中（Crawl4AI 等） |

---

## 已註冊來源

| id | 類型 | 說明 |
|----|------|------|
| `tianxi-database` | database | 讀取 tianxi-database raw CSV（不重複爬 HKJC） |
| `tianxi-api` | api | `https://www.tianxi.racing` TX-Oracle 預測 |

```bash
python -m ingestion.cli --list
python -m ingestion.cli --health tianxi-database
```

---

## 目錄

```text
domain-brain/
├── README.md
├── brain/                 # 天喜腦本地索引與查詢
├── ingestion/             # 來源 registry、CLI、runs/chunks/metrics
├── connectors/            # tianxi_db / tianxi_api /（可選 mem0）
├── agents/                # reflection 骨架
├── schemas/               # Source / CrawlRun JSON Schema
├── docs/
└── .github/workflows/     # 定時 ingest
```

---

## 設計原則

1. **先免費跑通邏輯**（方案 B）
2. 知識來源必須可列表、可健康監控、可選擇性增刪
3. 垂直數據護城河（tianxi）優先於通用框架
4. 日後若要更強檢索（向量／混合／託管），再作為可替換層接入，不綁死單一雲服務

---

## License

MIT
