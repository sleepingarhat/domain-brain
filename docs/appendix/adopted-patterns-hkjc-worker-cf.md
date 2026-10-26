# 採納圖案：jeffincn/hkjc-worker × Cloudflare skills → 天喜

> 授權：t63u／pt63u（2026-10-26）  
> **為己所用**＝讀懂別人圖案後，**改寫／組裝進天喜自己嘅 code／kb／jobs**；唔 vendor、唔當 runtime dependency、唔 mirror 整倉。  
> 政策：可開 PR；**唔 merge、唔 Lovable publish、唔改／rotate secrets**。獨立驗證。

## 1. 學到咩（具體規則）

1. **poll_ticks ≠ workflow success**  
   jeffincn 用 D1 `poll_ticks` 分開記 STATIC／MISSING／COLLECTION_FAILURE。GHA「綠燈」可以係 0 有用資料。天喜要有**內容層心跳**（`data/job_ticks/*.json` 或 `telegram_alert_state` 嘅 `job_tick:*`）。

2. **content-hash push dedupe**  
   相同 payload 唔重複推／唔重複告警。天喜派彩已有 `source_sha256`；缺口係「成個 job 停咗」——hash dedupe 掩蓋唔到 silent stall，要 tick 互補。

3. **watchdog rearm + circuit breaker**  
   告警要可恢復（recoveredAt）、同碼冷卻、錯碼即再發。天喜 `updateDividendAlert` 已近似；circuit 層面用「連續 fail tick → dead-man 紅」而唔係盲目重試打爆上游。

4. **GraphQL／採集忽略過去日期 + LOCAL_VENUES**  
   jeffincn `LOCAL_VENUES = ST|HV`，跳過境外 S1–S5。天喜 HTML 派彩已 skip「海外賽事」；會議索引層再濾一次 ST/HV（defence in depth）。

5. **CF Queues：ack-after-success、idempotency、DLQ**  
   成功先 ack；重試要幂等（穩定 PK／ON CONFLICT）。天喜 D1 odds push 已用穩定 id upsert；DLQ 圖案對照：失敗 tick + TG alert，而唔係另開 SaaS queue。

6. **CSV schema／最少列／必填欄（pandera／frictionless 精神，零依賴）**  
   淨係 row-count（舊 `assert_collected_rows`）睇唔到錯 header／截斷。新 `assert_csv_schema.py` 查必填欄、min rows、min distinct `race_no`、欄位填充率 ≥80%。

7. **healthchecks expected-by-T → 自建**  
   優先 `job_ticks` + GHA watchdog，唔強迫上 healthchecks.io。

## 2. 天喜而家差咩（對照）

| 圖案 | jeffincn / CF | 天喜改前 | 落地 |
|------|---------------|----------|------|
| 內容心跳 | poll_ticks | 多數靠 GHA conclusion | `job_ticks.py` + dividends `job_tick:*` |
| CSV schema | （自建 validation） | 只有 rows>0 | `assert_csv_schema.py` |
| venue 過濾 | LOCAL_VENUES | HTML skip 海外 | dividends 會議索引亦濾 ST/HV |
| hash dedupe | content-hash push | 派彩已有 sha256 | 保留，唔重複造輪 |
| Queues DLQ | CF Queues | TG alert + retry | 對照筆記；唔引入 CF Queue 依賴 |

## 3. 點落地（本輪 PR）

- **tianxi-racing**：`scripts/ci/assert_csv_schema.py`、`job_ticks.py`；加強 `assert_collected_rows.sh`（可選 `ASSERT_CSV`）；`capy_race_daily` 刮完 assert + record tick；`automation_watchdog` dead-man（未 seeded 只 warning）。
- **tianxi-web**：`src/lib/job-ticks.ts`；`racing-dividends` 寫 tick + LOCAL_VENUES 過濾。
- **kb**：本文 + MQTT 10-28 只讀計劃。

## 4. 授權／風險

- **授權**：抽圖案改寫；保留原專案名字作出處；唔 copy 大段 proprietary 業務邏輯當產品。
- **風險**：首次 merge 後 `job_ticks` 未 seeded → watchdog warning（設計如此）；schema min_rows 過嚴可能誤殺短場日——可用 `--min-rows`／workflow 參數調。
- **唔做**：merge／publish／改 secrets；vendor 整倉；MQTT 接 production／TG。

## 5. 驗收（用戶自行）

```bash
# racing
cd tianxi-racing && python3 -m unittest tests.test_assert_csv_schema tests.test_job_ticks -v
python3 scripts/ci/assert_csv_schema.py --csv data/2016/results_2016-07-10.csv --kind results
python3 scripts/ci/job_ticks.py record --job capy_race_daily --status ok
python3 scripts/ci/job_ticks.py check --job capy_race_daily --max-age-hours 36

# web
cd tianxi-web && npx vitest run src/lib/job-ticks.test.ts
```

手動：merge 後下一個賽日睇 `data/job_ticks/capy_race_daily.json` 有無更新；派彩 job response 含 `jobTick`。
