# Connectors

各類型知識來源連接器。

| 檔案 | 狀態 | 說明 |
|------|------|------|
| `tianxi_db.py` | ✅ | 讀取 tianxi-database raw CSV |
| `tianxi_api.py` | ✅ | 呼叫 TX-Oracle `/api/analyze/today-picks` |
| `mem0_push.py` | 可選骨架 | 長期記憶（非跑通必需） |
| `web_crawl*.py` | 規劃 | Crawl4AI 等 |
| `manual.py` | 規劃 | 人手上傳 |

每個 connector 輸出統一 chunks + metadata，並寫入 Crawl Run。  
Chunks 由 `brain.cli build` 納入天喜腦本地索引。
