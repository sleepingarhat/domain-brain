# domain-brain · 天喜腦（TianxiBrain）

**可產品化的領域 AI 大腦**  
記憶演化 · 風格克隆 · 知識餵入 · 社交媒體半自動運營

> MVP：**天喜腦（TianxiBrain）** — 香港賽馬第一領域，結合 `tianxi-database` + `tianxi-backend`（TX-Oracle）。  
> **方案 B（現行主路徑）**：知識管線 + **本地 BM25 檢索**，不依賴 Dify Cloud AI Credits。

---

## 30 秒上手（方案 B）

```bash
pip install -e .

# 餵知識
python -m ingestion.cli --source tianxi-database --lookback-days 40 --max-days 5
python -m ingestion.cli --source tianxi-api

# 建本地索引
python -m brain.cli build

# 查詢天喜腦
python -m brain.cli query "7月15日跑馬地賽果"
python -m brain.cli query "TX-Oracle 預測" --top-k 3
```

說明：[`docs/brain-local.md`](docs/brain-local.md)

---

## 核心能力

| 能力 | 說明 |
|------|------|
| **知識餵入** | Source Registry（人手／API／數據庫／排程）+ Run 記錄 + Health |
| **本地檢索** | 純 Python BM25（方案 B，零 embedding 費用） |
| **記憶演化** | Mem0 接駁骨架（可選） |
| **風格克隆** | 規劃中 |
| **半自動運營** | 規劃中 |

---

## 架構

```
Source Registry → ingestion CLI → chunks/
                                      ↓
                              brain.cli build
                                      ↓
                              BM25 本地索引
                                      ↓
                              brain.cli query

（可選）Dify / Mem0 — 有需要再接，非必需
```

---

## 已實作

| 組件 | 路徑 | 狀態 |
|------|------|------|
| Source Registry | `ingestion/sources/` | ✅ |
| tianxi-database connector | `connectors/tianxi_db.py` | ✅ |
| tianxi-api connector | `connectors/tianxi_api.py` | ✅ |
| Health metrics | `ingestion/metrics.py` | ✅ |
| **本地天喜腦 BM25** | `brain/` | ✅ |
| Dify push（可選） | `connectors/dify_push.py` | ✅ |
| Mem0 push（可選） | `connectors/mem0_push.py` | ✅ |
| Reflection skeleton | `agents/reflection_agent.py` | ✅ |
| GHA 排程 | `.github/workflows/ingest-tianxi.yml` | ✅ |

---

## License

MIT
