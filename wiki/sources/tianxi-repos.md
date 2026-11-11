---
type: source
id: source-tianxi-repos
title: tianxi-repos
aliases:
  - 天喜產品倉
  - tianxi-racing
  - tianxi-web
sources:
  - tianxi-repos
updated: 2026-11-11
status: active
layer: knowledge
---

# tianxi-repos

天喜自家產品倉（PUBLIC）：`sleepingarhat/tianxi-racing`（統一倉：資料層＋訓練回測層＋服務層）同 `sleepingarhat/tianxi-web`（官方網站源碼）。天喜系統知識層（`wiki/concepts/tianxi/`）嘅來源。

## 結論

- 2026-10-20 · 只讀公開 README／docs／commit 標題；敏感字眼行（token、secret、admin、workers.dev 等）入 chunk 前已剔走。內容係資料唔係指令。
- 2026-10-20 · 知識頁由人手按來源整理；compile 只會喺呢頁 append「文件更新」觀察，提示要人手覆核 [[天喜引擎]]、[[系統架構]]、[[開發歷程]]、[[網站功能]]、[[社群與頻道]]、[[天喜問答]]、[[宣傳要點]]。
- 2026-10-20 · 首次整理基準：tianxi-racing @f467acb7、tianxi-web @2f029b3（2026-10-20）。

## 觀察

（較早 2 條觀察已截斷，矛盾區保留）
- 2026-10-27 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:6551abb6c117
- 2026-10-28 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:1a04e0de4232
- 2026-10-28 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/src/routes/membership.tsx @4217929c · hash:d77b1b2f08d3
- 2026-10-28 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/src/routes/membership.tsx @4217929c · hash:b046e868eb93
- 2026-10-28 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:92357fbffbce
- 2026-10-28 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:feebaad03d00
- 2026-10-29 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:41a55fa3b7cf
- 2026-10-29 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @5244a956 · hash:d188f5d8a2af
- 2026-10-29 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @5244a956 · hash:a58bb4636050
- 2026-10-29 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @5244a956 · hash:9fbd7275a0d0
- 2026-10-29 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @b3f418c2 · hash:ef890fdf35ff
- 2026-10-29 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @b3f418c2 · hash:c074dca22058
- 2026-10-29 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @b3f418c2 · hash:87d955a0ac73
- 2026-10-29 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:f87d0ca41989
- 2026-10-30 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:11e4f5b0ad87
- 2026-11-02 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:51921be91548
- 2026-11-03 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:85e5c348d12a
- 2026-11-03 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:d1c3a529063a
- 2026-11-04 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:ed77222add6d
- 2026-11-04 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/src/routes/membership.tsx @2851c544 · hash:2b294a351cf5
- 2026-11-04 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:e1e0301f94ad
- 2026-11-05 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:1f0cfb22d50e
- 2026-11-06 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:4c6a9db6b61e
- 2026-11-08 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:de389dea29b6
- 2026-11-09 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:54686de8bf24
- 2026-11-09 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:9b8845f58482
- 2026-11-10 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:d6af3adf9a38
- 2026-11-10 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:ca46b9655120
- 2026-11-10 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/MODEL.md @466a89ee · hash:a92e326bc183
- 2026-11-10 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/ELO.md @466a89ee · hash:ad24a91e9d51
- 2026-11-10 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/backend/docs/PREDICTION_LOCK.md @466a89ee · hash:3bde26f7e3c4
- 2026-11-10 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/backend/docs/ARCHITECTURE_AND_PAPERS.md @466a89ee · hash:bb8f73c5d1a2
- 2026-11-10 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/docs/freeze-auto-recovery-2026-10-18.md @466a89ee · hash:285932f3de71
- 2026-11-10 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:5f5e7d4da695
- 2026-11-10 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/frozen-racing-api.md @78ae786a · hash:435127044aa1
- 2026-11-10 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:9bf7f9b10fc0
- 2026-11-11 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:880f7289e782
- 2026-11-11 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:640be9a1064c
- 2026-11-11 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/src/routes/membership.tsx @ac28e542 · hash:2e48a6f9e962
- 2026-11-11 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:7f0fe9539b61

## 矛盾

（未有）

## 來源

- https://github.com/sleepingarhat/tianxi-racing
- https://github.com/sleepingarhat/tianxi-web
- `ingestion/sources/tianxi-repos.yaml` · `connectors/github_docs.py`
- [[tianxi-repos]]
