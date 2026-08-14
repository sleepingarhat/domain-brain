# Knowledge Ingestion Layer

統一知識餵入層。支援人手、API、數據庫、定期自動爬取，並以 **Source Registry** 作為唯一管理真相來源。

此設計直接對應未來產品前端的「知識來源管理」頁面。

---

## 1. 設計目標

- 清晰可管理的來源清單（可選擇性增加 / 刪除 / 啟停）
- 每次執行都有完整記錄（Crawl Run）
- 可量化的有效性與穩定性指標（Health Metrics）
- 多類型來源統一抽象
- 產出可直接進入 Dify Knowledge Base + Mem0

---

## 2. 三層資料模型

### 2.1 Source Registry（來源清單）

每個來源的永久設定。

必要欄位見 `schemas/source-registry.schema.json`。

重點：

- `id`：穩定唯一識別
- `type`：`web_crawl` | `rss` | `api` | `database` | `manual`
- `enabled`：即時開關
- `schedule`：cron 表達式（可選）
- `domain_tags`：領域標籤（方便過濾）
- `priority`：執行優先級
- `config`：類型專屬設定

### 2.2 Crawl Run（執行記錄）

每一次實際執行的日誌。

```yaml
run_id: "20260814-083012-tianxi-db"
source_id: "tianxi-database"
started_at: "2026-08-14T08:30:12+08:00"
finished_at: "2026-08-14T08:30:28+08:00"
status: "success"          # success | partial | failed | skipped
items_fetched: 12
items_new: 7
items_updated: 3
items_skipped: 2
error_message: null
duration_seconds: 16.2
content_hash: "sha256:..." # 用於偵測是否有真正新內容
```

### 2.3 Health Metrics（健康指標）

由近期 Runs 聚合而來，供前端狀態燈與告警使用。

建議指標：

| 指標 | 說明 |
|------|------|
| success_rate_7d / 30d | 最近成功率 |
| consecutive_failures | 連續失敗次數 |
| last_success_at | 最後成功時間（新鮮度） |
| avg_items_new | 平均每次新增知識量 |
| avg_duration_seconds | 平均耗時 |
| content_change_rate | 內容實際變化比例 |

前端可直接顯示：
- 綠色 / 黃色 / 紅色狀態
- 「最近成功：2 小時前」
- 「30 日成功率：94%」
- 「建議處理：連續失敗 3 次」

---

## 3. 來源類型與優先級（馬神 MVP）

| 優先級 | type | 來源 | 說明 |
|--------|------|------|------|
| P0 | `database` / `api` | tianxi-database + tianxi-backend | 結構化賽果、排位、預測、ELO。不重複爬 HKJC |
| P1 | `manual` | 風格樣本、ebook、分析筆記 | 人手餵入，進入同一 Registry |
| P1 | `web_crawl` | 選定賽馬分析網站 / 公開文章 | Crawl4AI 或 Firecrawl |
| P2 | `rss` | 相關 RSS | 輕量補充 |
| P2 | `api` | 其他外部 API | 按需擴展 |

---

## 4. 與 Dify / Mem0 的接駁

1. Connector 產出乾淨 Markdown / 結構化 chunks + metadata
2. 寫入 Dify Knowledge Base（透過 API 或 Knowledge Pipeline）
3. 重要事實 / 反思結果同步寫入 Mem0（長期記憶演化）
4. Source Registry 的 `id` 與 metadata 會帶入 chunk，方便溯源與前端過濾

---

## 5. 調度建議

- 結構化 tianxi 數據：跟隨 tianxi 既有 GHA 節奏，或賽日後觸發
- web_crawl / rss：GitHub Actions cron 或 Cloudflare Cron Triggers
- 手動來源：前端上傳後即時觸發一次 ingestion

---

## 6. 未來前端對應

「知識來源管理」頁面預期功能：

- 來源列表（搜尋、標籤過濾、狀態過濾）
- 每行：名稱、類型、狀態燈、最後成功時間、成功率、啟停開關
- 詳情：設定、最近 Runs、錯誤日誌
- 操作：新增、編輯、暫停/啟用、刪除、手動觸發
- 批量操作

本層資料模型一開始就為這個 UI 設計。
