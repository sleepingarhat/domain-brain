# 完場反思

只對綠燈完場賽日寫 wiki。禁止回測充場。

## 綠燈

同時成立：

1. `race_date` ≤ 今日（香港）
2. chunks 有 `tianxi-database` 單場賽果（`artefact=results_race` 或內文「單場賽果」）
3. 至少一匹馬有名次

不算綠燈：today-picks 独自、hit-rate、未來賽日、只有總覽無名次。

當日 TX-Oracle chunks 可缺。缺就只寫賽果觀察，矛盾欄記「未回測充場」。

## 指令

```bash
python -m ingestion.cli --source tianxi-database --lookback-days 14 --max-days 3
python -m brain.cli compile
python -m brain.cli reflect                  # 視窗內最近 2 個綠燈日
python -m brain.cli reflect --date 2026-09-21
python -m brain.cli build
```

預設 `--lookback-days 5 --max-days 2`。唔好一次掃整季。

## 寫哪

- `wiki/synthesis/race-YYYY-MM-DD.md`
- 相關 `wiki/entities/horses/`
- `wiki/concepts/冷熱偏.md`

凍結預測檔不動。
