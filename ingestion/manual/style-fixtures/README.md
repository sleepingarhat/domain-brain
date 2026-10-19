# 人手風格樣本

把認可過嘅粵語評述 `.md` / `.txt` 放呢度（唔好貼有版權爭議嘅全文）。
之後喺 `ingestion/sources/style-commentators.yaml` 開 `style-example-manual`，或者：

```bash
python -m ingestion.cli --feed-file ingestion/manual/style-fixtures/我的樣本.md --title "樣本"
# 然後手動將 chunk metadata 標 purpose=style，或用 style-example-manual source
python -m brain.cli style-build
```
