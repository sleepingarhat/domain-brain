# domain-brain · 天喜腦（TianxiBrain）

**可產品化的領域 AI 大腦（免費本地路徑）**  
知識餵入 · 來源管理 · 本地檢索 · 可選 LLM 一句答覆

> 產品名：**天喜腦（TianxiBrain）**  
> 第一領域：香港賽馬（`tianxi-database` + TX-Oracle）  
> **方案 B**：本機 / GitHub Actions 免費跑通，不依賴雲端知識庫付費額度。

---

## 30 秒跑通

```bash
git clone https://github.com/sleepingarhat/domain-brain.git
cd domain-brain
pip install -e .

# 1) 餵知識（賽果會產出中文場次摘要）
python -m ingestion.cli --source tianxi-database --lookback-days 40 --max-days 5
python -m ingestion.cli --source tianxi-api

# 2) 建本地索引
python -m brain.cli build

# 3) 查詢
python -m brain.cli query "7月15日跑馬地第1場"
python -m brain.cli query "架勢奇爸" --top-k 3

# 4) 可選：自備 API key 生成精簡答覆
# export OPENAI_API_KEY=...
# export OPENAI_BASE_URL=https://api.openai.com/v1   # 或 Groq 等兼容接口
# export OPENAI_MODEL=gpt-4o-mini
python -m brain.cli query "7月15日第一場誰贏" --answer
```

說明：[docs/brain-local.md](docs/brain-local.md) · [docs/knowledge-ingestion.md](docs/knowledge-ingestion.md)

---

## 每日自動（GitHub Actions）

Workflow：`.github/workflows/ingest-tianxi.yml`

- 排程：每天 01:30 HKT（`30 17 * * *` UTC）
- 亦可手動 **Actions → TianxiBrain daily ingest + index → Run workflow**
- 步驟：`tianxi-database` → `tianxi-api` → `brain.cli build` → 上傳 artefacts（14 日）

---

## 架構

```text
Source Registry → ingestion CLI → 中文 chunks
                                      ↓
                              brain.cli build（BM25）
                                      ↓
                         query ／ query --answer（可選 LLM）
```

---

## 核心能力

| 能力 | 現狀 |
|------|------|
| 知識餵入 + Health | ✅ |
| 賽果中文摘要（按日／按場） | ✅ |
| TX-Oracle 中文預測摘要 | ✅ |
| 本地 BM25 檢索 | ✅ |
| 每日 GHA ingest + build | ✅ |
| 可選 LLM 答覆（`--answer`） | ✅ 需自備 key |
| Mem0 / 反思 Agent | 骨架（可選） |

---

## 已註冊來源

| id | 類型 | 說明 |
|----|------|------|
| `tianxi-database` | database | raw CSV 賽果 |
| `tianxi-api` | api | `https://www.tianxi.racing` 預測 |

---

## 設計原則

1. 先免費跑通邏輯  
2. 來源可列表、可監控、可增刪  
3. tianxi 數據護城河優先  
4. 更強檢索／模型日後可替換接入

---

## License

MIT
