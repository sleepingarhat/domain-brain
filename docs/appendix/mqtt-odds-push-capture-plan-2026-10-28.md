# MQTT odds push：2026-10-28 只讀 capture 計劃

> 出處對照：`astroboy-ai/hkjc-racing-api-study`（`docs/odds_push.md`）  
> **今輪唔接 TG、唔接 production broker。** 只設計筆記 + 驗證日計劃。

## 目標

喺 2026-10-28（或最近一個 HV／ST 夜馬）做**只讀** capture，確認 HKJC Solace／MQTT odds push 契約（topic、payload 欄位、更新頻率），之後先決定係咪值得做天喜旁路（旁路 ≠ 取代現有 GraphQL collector）。

## 非目標（刻意）

- 唔改 tianxi-web／racing production collector
- 唔接 Telegram 告警
- 唔寫 credential 入 repo；唔 rotate 現有 secrets
- 唔下注、唔改產品策略（Bobosky／JonzieLo 只 kb 對照）

## 前置

1. 讀 `astroboy` 公開文件：broker host、topic pattern、QoS、訊息 JSON 形狀。
2. 用**獨立** throwaway 環境變數（本機或隔離 box），唔共用天喜 GHA secrets。
3. 確認當日 `fixture_guard` 係 HV 或 ST 本地場。

## 當日步驟（只讀）

1. **T-30min**：開 capture 腳本（stdout + 本地檔 `/tmp/mqtt-capture-YYYYMMDD.jsonl`），訂閱公開／文件所述 odds topic。
2. **開跑後 15–30 min**：抽樣 3 個 race_no，對照同期 GraphQL snapshot（天喜 `capy_odds` 或手動 query）——欄位映射表寫入本檔「結果」節。
3. **收工**：停訂閱；檔案**唔 commit**（可能含敏感路由）；只把**去識別**後嘅 schema 摘要 append 去本 kb。
4. **結論**：值得做旁路？只係 enrichment？定維持 GraphQL-only？

## 結果（10-28 後填）

- Broker／topic：（待填）
- Payload 必填欄：（待填）
- 同 GraphQL 差異：（待填）
- 建議：（待填）

## 風險

- Broker ACL／ToS：只讀、短窗、唔轉發第三方。
- 誤接 production：禁止用天喜 cron token 或 Lovable publish 路徑。
