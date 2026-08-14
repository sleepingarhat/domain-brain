# Connectors

各類型知識來源連接器實作位置。

規劃：

- `tianxi_db.py` — 讀取 tianxi-database raw CSV
- `tianxi_api.py` — 呼叫 tianxi-backend 預測 / 分析 API
- `web_crawl4ai.py` — 使用 Crawl4AI 的 web_crawl 實作
- `manual.py` — 人手上傳處理

每個 connector 應輸出統一格式的 chunks + metadata，並寫入 Crawl Run 記錄。
