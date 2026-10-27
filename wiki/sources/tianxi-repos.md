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
updated: 2026-10-27
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
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @7ecf1bf0 · hash:7faff39f4af8
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/backend/README.md @7ecf1bf0 · hash:ca3af9d62312
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:c6ac660b0b80
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/README.md @dea9697d · hash:249264019019
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @dea9697d · hash:940c1fe45be9
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @dea9697d · hash:7ab00c58ea43
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @dea9697d · hash:3d0963369b24
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/reviews/repository-consistency-2026-10-24.md @dea9697d · hash:7265d5ce0317
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/src/lib/freeStage.ts @dea9697d · hash:d9c4a37b2841
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/src/lib/entitlement.ts @dea9697d · hash:bd75e5496751
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/src/routes/membership.tsx @dea9697d · hash:2d623e725f0e
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:6c23a9ae7977
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:549d8b81414c
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @9f3fb0f2 · hash:84937564cfa7
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @9f3fb0f2 · hash:e6517fe5d37e
- 2026-10-25 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @9f3fb0f2 · hash:3feaf6f7fb49
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:644cc4fe93c9
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @6f4a28fd · hash:ed0e5c35939c
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @6f4a28fd · hash:04aa80c3c148
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @6f4a28fd · hash:03193ed96aad
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:9102173e34e1
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @ff71218e · hash:2f523c570c98
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @ff71218e · hash:508f66a705df
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @ff71218e · hash:291a4b7c72e0
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @ff71218e · hash:d06f6a68ab6c
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/README.md @ff71218e · hash:5e53de279389
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:a523a60e49e1
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @37502043 · hash:a539afaeb9ee
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @37502043 · hash:bf630cb4d649
- 2026-10-26 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @37502043 · hash:acdc1d5262e2
- 2026-10-27 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:b69110787e6e
- 2026-10-27 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @0a50db2b · hash:355c1c274bb6
- 2026-10-27 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/src/routes/membership.tsx @0a50db2b · hash:03eb973c4686
- 2026-10-27 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/src/routes/membership.tsx @0a50db2b · hash:a07545932543
- 2026-10-27 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:2cf094c426c3
- 2026-10-27 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-racing/(git log) · hash:0c0e2a740729
- 2026-10-27 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @63b50b04 · hash:ad1ffb19e682
- 2026-10-27 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @63b50b04 · hash:7937e0753695
- 2026-10-27 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/docs/blueprint/tianxi-racing-blueprint-2026-10-13.md @63b50b04 · hash:0e278e8e0c08
- 2026-10-27 · tianxi-repos · 文件  — 文件更新 sleepingarhat/tianxi-web/(git log) · hash:6551abb6c117

## 矛盾

（未有）

## 來源

- https://github.com/sleepingarhat/tianxi-racing
- https://github.com/sleepingarhat/tianxi-web
- `ingestion/sources/tianxi-repos.yaml` · `connectors/github_docs.py`
- [[tianxi-repos]]
