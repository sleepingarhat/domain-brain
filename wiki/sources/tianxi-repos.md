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
updated: 2026-10-22
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

- 2026-10-20 · tianxi-repos · 開頁：首次人手整理，來源快照 tianxi-racing f467acb7、tianxi-web 2f029b3；公開 API engine-health／freeze-ledger／lock-state／frozen-racing 2026-10-20 讀取。 · hash:2c76e22813b7
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @f467acb7 · hash:67a9a9939526
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @f467acb7 · hash:2de117f54bf6
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @f467acb7 · hash:69774812cbea
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @f467acb7 · hash:8a0f0f00ff0c
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/MODEL.md @f467acb7 · hash:3af26e4d9c7f
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/ELO.md @f467acb7 · hash:4f795c29f3b3
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/backend/README.md @f467acb7 · hash:271717c4c5cd
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/backend/docs/PREDICTION_LOCK.md @f467acb7 · hash:d4c6f13cc1dc
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/backend/docs/ARCHITECTURE_AND_PAPERS.md @f467acb7 · hash:89b269a3fef2
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/docs/freeze-auto-recovery-2026-10-18.md @f467acb7 · hash:afcb3660c1d6
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:2feb6eced9ca
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/README.md @2f029b31 · hash:84967b9659e1
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @2f029b31 · hash:33dfca71a0ac
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @2f029b31 · hash:53ad67645102
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/frozen-racing-api.md @2f029b31 · hash:810e9fdffd25
- 2026-10-20 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:f65744ebb9ec
- 2026-10-21 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:38c0698fc095
- 2026-10-21 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @7a0766f1 · hash:248c800f95a3
- 2026-10-21 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @7a0766f1 · hash:4e4a48a112b6
- 2026-10-21 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:52a80f2e128e
- 2026-10-21 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:2b11cd36af5d
- 2026-10-21 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @45392cfd · hash:e03957906bda
- 2026-10-21 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @45392cfd · hash:fd73c64e370e
- 2026-10-21 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:65232edd89e3
- 2026-10-22 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:f97b352a2f8b
- 2026-10-22 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @c9d8a3fb · hash:aa545b6660f7
- 2026-10-22 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @c9d8a3fb · hash:65f0a80bc848
- 2026-10-22 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @c9d8a3fb · hash:bd32d51a5ffc
- 2026-10-22 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:764bb621d0bb

## 矛盾

（未有）

## 來源

- https://github.com/sleepingarhat/tianxi-racing
- https://github.com/sleepingarhat/tianxi-web
- `ingestion/sources/tianxi-repos.yaml` · `connectors/github_docs.py`
- [[tianxi-repos]]
