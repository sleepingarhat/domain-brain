# 自動化

主課程：`Brain Daily`（`.github/workflows/00-brain-daily.yml`）。

風格克隆、社交發佈、凍結預測檔 **不自動**。

## 時間表（HKT）

| 時間 | slot | 做哎 |
|------|------|------|
| 12:00 | card | `tianxi-api` today-picks → compile → commit `wiki/` + `ingestion/chunks/` |
| 01:30 | results | `tianxi-database` + 公開評論 → compile → reflect（5 日視窗、最多 2 個綠燈日）→ build/lint/eval → commit |

無賽日：reflect skip，不失敗。無變化不 commit。

## 點解要 commit chunks

`tianxi-api` 只有「今日精選」。中午唔落盤，凌晨反思就配唔到預測樣本。
chunks 保 21 日。index 不入倉。

## 手動

Actions → **Brain Daily** → Run workflow → `card` / `results` / `full`。

舊的 01 / 02 / 03 保 `workflow_dispatch`，日程已關，免重複跑。
