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

| `style_crawl.py` | ✅ | 評馬人文章（trafilatura，fallback web_static；robots + rate limit） |
| `youtube_subs.py` | ✅ | YouTube 自動字幕（yt-dlp；zh-HK/yue/zh-Hant） |

風格來源要喺 registry 標 `domain_tags: [style]` 或 `config.purpose: style`。見 `docs/style-exemplars.md`。
| `github_docs.py` | ✅ | `tianxi-repos`：公開倉 README／docs／commit 標題（敏感行剔走、只寫有變動）。見 `docs/tianxi-system-knowledge.md` |
