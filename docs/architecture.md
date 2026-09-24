# 天喜腦架構

兩層分開。知識層永久；項目層會冷。預測凍結唔入 wiki。

```text
tianxi-database / TX-Oracle          HKJC / 馬經 / 人手筆記
        │                                    │
        ▼                                    ▼
  結構化事實（表、凍結）              ingestion/chunks（原文）
        │                                    │
        │                         compile（只 append）
        │                                    ▼
        │                         wiki entities + 矛盾時間線
        └─────────────┬─────────────────────┘
                       ▼
              retrieve：BM25（原文）+ 實體頁（理解）
                       ▼
              query / 賽後反思 / （可選）社交草稿
```

## 模組

| 路徑 | 角色 | 可寫？ |
|------|------|--------|
| `ingestion/` | 來源 registry、crawl、chunks | 是（ingest） |
| `brain/store.py` + `retrieve.py` | BM25 語料同檢索 | 索引檔 |
| `brain/compile.py` + `wiki/` | 實體編譯、矛盾、日誌 | 只 `wiki/` |
| `brain/lint_wiki.py` | 頁契約 | 否 |
| `eval/golden.json` | 黃金問題 | 否 |
| `agents/reflection_agent.py` | 預測 vs 賽果 → synthesis／馬頁 | 只 `wiki/` |
| `connectors/mem0_push.py` | 可選外掛記憶 | 否（預設關） |

## 規則來源

編譯契約寫死嗎 `wiki/RULES.md`：一頁一實體、矛盾不覆蓋、預測標觀察、無人值守只准 append。

## 指令

```bash
python -m ingestion.cli --source tianxi-database --lookback-days 40 --max-days 5
python -m brain.cli compile
python -m brain.cli build
python -m brain.cli lint
python -m brain.cli eval
python -m brain.cli query "跑馬地第1場" --layer all
python -m brain.cli query "場地適性" --layer wiki
```

順序：ingest → compile → build。Build 會把 wiki 頁一併入 BM25。
