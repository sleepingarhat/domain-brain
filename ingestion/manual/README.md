# 人手餵知識資料夾

把 `.md` 或 `.txt` 放喺呢度，然後跑：

```bash
python -m ingestion.cli --feed-dir ingestion/manual
python -m brain.cli build
```

或者單檔：

```bash
python -m ingestion.cli --feed-file ingestion/manual/我的賽評.md --title "我的賽評"
python -m brain.cli build
```
