# domain-brain · 天喜腦（TianxiBrain）

**可產品化的領域 AI 大腦（免費本地路徑）**  
知識饋入 · wiki 編譯（記憶演化） · 本地檢索 · agent 管治 · 可選 LLM 一句答覆

> 產品名：**天喜腦（TianxiBrain）**  
> 第一領域：香港賽馬（`tianxi-database` + TX-Oracle）  
> **方案 B**：本機 / GitHub Actions 免費跑通。

---

## 自動（GitHub Actions）

[![Brain Daily](https://github.com/sleepingarhat/domain-brain/actions/workflows/00-brain-daily.yml/badge.svg)](https://github.com/sleepingarhat/domain-brain/actions/workflows/00-brain-daily.yml)

| Workflow | HKT | 做哎 |
|----------|-----|------|
| **Brain Daily** `card` | 12:00 | 收 today-picks，compile，commit wiki + chunks |
| **Brain Daily** `results` | 01:30 | 賽果 + 評論 → compile → reflect → build，commit 記憶 |

詳見 [docs/automation.md](docs/automation.md)。  
風格草稿、社交發佈、凍結預測 **不自動**。

舊的 01 / 02 / 03 只保手動跑。

---

## 30 秒跑通

```bash
git clone https://github.com/sleepingarhat/domain-brain.git
cd domain-brain
pip install -e .

python -m ingestion.cli --source tianxi-database --lookback-days 40 --max-days 5
python -m ingestion.cli --source tianxi-api
python -m brain.cli compile
python -m brain.cli reflect
python -m brain.cli build
python -m brain.cli query "7月15日跑馬地第1場"
python -m brain.cli query "場地適性" --layer wiki
```

---

## 架構

```text
Source Registry → ingestion / crawl → chunks
                                      ↓
                              compile（wiki，只 append）
                                      ↓
                              reflect（綠燈完場才寫）
                                      ↓
                              build（BM25）
```

凍結預測不入 compile。矛盾寫低、唔覆蓋。

---

## License

MIT
