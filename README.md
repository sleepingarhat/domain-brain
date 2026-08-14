# domain-brain · 天喜腦（TianxiBrain）

**可產品化的領域 AI 大腦（免費本地路徑）**  
知識餵入 · 來源管理 · 本地檢索 · 可選 LLM 一句答覆

> 產品名：**天喜腦（TianxiBrain）**  
> 第一領域：香港賽馬（`tianxi-database` + TX-Oracle）  
> **方案 B**：本機 / GitHub Actions 免費跑通，不依賴雲端知識庫付費額度。

---

## 監察（GitHub Actions）

同 `tianxi-database` 一樣，用 workflow badge 睇通過／失敗：

[![Ingest Tianxi Data](https://github.com/sleepingarhat/domain-brain/actions/workflows/01-ingest-tianxi-data.yml/badge.svg)](https://github.com/sleepingarhat/domain-brain/actions/workflows/01-ingest-tianxi-data.yml)
[![Crawl Free Commentary](https://github.com/sleepingarhat/domain-brain/actions/workflows/02-crawl-commentary.yml/badge.svg)](https://github.com/sleepingarhat/domain-brain/actions/workflows/02-crawl-commentary.yml)
[![Build Brain Index](https://github.com/sleepingarhat/domain-brain/actions/workflows/03-build-brain-index.yml/badge.svg)](https://github.com/sleepingarhat/domain-brain/actions/workflows/03-build-brain-index.yml)

| Workflow | 做咩 | 排程（HKT） |
|----------|------|-------------|
| **Ingest Tianxi Data** | `tianxi-database` + `tianxi-api` | 每日 01:30 |
| **Crawl Free Commentary** | HKJC / Idol Horse / The Standard | 每日 01:40 |
| **Build Brain Index** | `brain.cli build` | 每日 01:50 或上游完成後 |

手動跑：Repo → **Actions** → 揀對應 workflow → **Run workflow**  
詳細 run 記錄、log、artefacts 都喺 Actions 頁。

本機睇來源健康：

```bash
python -m ingestion.cli --list
python -m ingestion.cli --health tianxi-database
python -m ingestion.cli --health hkjc-news
```

---

## 30 秒跑通

```bash
git clone https://github.com/sleepingarhat/domain-brain.git
cd domain-brain
pip install -e .

python -m ingestion.cli --source tianxi-database --lookback-days 40 --max-days 5
python -m ingestion.cli --source tianxi-api
python -m brain.cli build
python -m brain.cli query "7月15日跑馬地第1場"
```

說明：[docs/brain-local.md](docs/brain-local.md) · [docs/knowledge-ingestion.md](docs/knowledge-ingestion.md)

---

## 架構

```text
Source Registry → ingestion / crawl → chunks
                                      ↓
                              brain.cli build（BM25）
                                      ↓
                         query ／ query --answer（可選 LLM）
```

---

## 已註冊來源

| id | 自動 | 說明 |
|----|------|------|
| `tianxi-database` | ✅ | 賽果 CSV |
| `tianxi-api` | ✅ | TX-Oracle 預測 |
| `hkjc-news` | ✅ | 馬會公開資訊／新聞 |
| `idol-horse` | ✅ | Idol Horse 專題 |
| `the-standard-inside-track` | ✅ | Standard 賽馬頁 |
| 報章馬經等 | ❌ | 非免費穩定全文，registry 保留但關閉 |

---

## License

MIT
