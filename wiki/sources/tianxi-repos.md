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
updated: 2026-11-22
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
- 2026-11-12 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:978f861b2b93
- 2026-11-12 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:38dd794a1012
- 2026-11-15 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/backend/README.md @1aa3f621 · hash:9623152edfda
- 2026-11-15 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/README.md @73c5cb00 · hash:615a7e88f05d
- 2026-11-15 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/reviews/repository-consistency-2026-10-24.md @73c5cb00 · hash:b5f5ca74019b
- 2026-11-15 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/src/lib/freeStage.ts @73c5cb00 · hash:4e4bcfebd794
- 2026-11-15 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/src/lib/entitlement.ts @73c5cb00 · hash:f862cdf96d17
- 2026-11-16 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @69eb1e43 · hash:173315fa19d3
- 2026-11-16 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @69eb1e43 · hash:58e7530dcbae
- 2026-11-16 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @69eb1e43 · hash:465dfe573b1f
- 2026-11-16 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @69eb1e43 · hash:62964369e7bc
- 2026-11-16 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @69eb1e43 · hash:b9062c03a512
- 2026-11-17 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:b5038e7b8902
- 2026-11-18 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:2f5d5fcfa094
- 2026-11-18 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/src/routes/membership.tsx @434db609 · hash:72873be43dc2
- 2026-11-19 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @434db609 · hash:0e16ce1e376e
- 2026-11-19 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @434db609 · hash:45b03be0510d
- 2026-11-19 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @434db609 · hash:e51db4e0f1f5

## 矛盾

（未有）

## 來源

- https://github.com/sleepingarhat/tianxi-racing
- https://github.com/sleepingarhat/tianxi-web
- `ingestion/sources/tianxi-repos.yaml` · `connectors/github_docs.py`
- [[tianxi-repos]]
