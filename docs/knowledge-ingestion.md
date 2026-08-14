# Knowledge Ingestion Layer

統一知識餵入層。支援人手、API、數據庫、定期自動爬取，並以 **Source Registry** 作為唯一管理真相來源。

產出的 chunks 進入 **天喜腦本地檢索**（`brain/`，BM25）。  
此設計直接對應未來產品前端的「知識來源管理」頁面。

---

## 1. 設計目標

- 清晰可管理的來源清單（可選擇性增加 / 刪除 / 啟停）
- 每次執行都有完整記錄（Crawl Run）
- 可量化的有效性與穩定性指標（Health Metrics）
- 多類型來源統一抽象
- 產出可直接被 `brain.cli build` 索引

---

## 2. 三層資料模型

### 2.1 Source Registry（來源清單）

每個來源的永久設定。必要欄位見 `schemas/source-registry.schema.json`。

重點：

- `id`：穩定唯一識別
- `type`：`web_crawl` | `rss` | `api` | `database` | `manual`
- `enabled`：即時開關
- `schedule`：cron 表達式（可選）
- `domain_tags`：領域標籤
- `priority`：執行優先級
- `config`：類型專屬設定

### 2.2 Crawl Run（執行記錄）

每一次實際執行的日誌（見 `schemas/crawl-run.schema.json`）。

### 2.3 Health Metrics（健康指標）

由近期 Runs 聚合，供前端狀態燈與告警使用：success_rate、consecutive_failures、last_success_at、avg_items_new 等。

---

## 3. 來源類型與優先級（天喜腦 MVP）

| 優先級 | type | 來源 | 說明 |
|--------|------|------|------|
| P0 | `database` / `api` | tianxi-database + tianxi-backend | 結構化賽果、預測。不重複爬 HKJC |
| P1 | `manual` | 風格樣本、分析筆記 | 人手餵入 |
| P1 | `web_crawl` | 選定公開文章 | 規劃中 |
| P2 | `rss` / 其他 `api` | 補充源 | 按需 |

---

## 4. 與本地天喜腦的接駁

1. Connector 產出 chunks（title + content + metadata）
2. 寫入 `ingestion/chunks/<run_id>.json` 與 Crawl Run
3. `python -m brain.cli build` 重建 BM25 語料
4. `python -m brain.cli query "…"` 檢索

Source `id` 會留在 chunk metadata，方便溯源。

---

## 5. 調度

- 結構化 tianxi：GitHub Actions（見 `.github/workflows/ingest-tianxi.yml`）
- 手動來源：上傳後觸發一次 ingestion + rebuild index

---

## 6. 未來前端對應

「知識來源管理」：列表、狀態燈、成功率、啟停、手動觸發、增刪。  
本層資料模型一開始就為這個 UI 設計。
