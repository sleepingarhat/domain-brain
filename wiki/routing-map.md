---
type: meta
id: wiki-routing-map
title: Routing Map
aliases:
  - routing
sources: []
updated: 2026-09-24
status: evergreen
layer: knowledge
---

# Routing Map

Compile／reflection／人手寫入前對呢張表。唔好開重複實體。

## 結論

- 2026-09-24 · 一頁一實體。賽事唔開永久頁。凍結預測永不入 wiki 當事實。

## 觀察

| 內容 | 去邊 | 規則 |
| --- | --- | --- |
| 馬 | `wiki/entities/horses/<slug>.md` | 一馬一頁；新來源 append 觀察 |
| 騎師 | `wiki/entities/jockeys/<slug>.md` | 同上 |
| 練馬師 | `wiki/entities/trainers/<slug>.md` | 同上 |
| 場地（跑馬地／沙田／谷草等） | `wiki/entities/courses/<slug>.md` | 同上 |
| 場地適性、冷熱偏、檔位等概念 | `wiki/concepts/<名>.md` | 已有就鏈，唔開近義重複頁 |
| 來源（tianxi-database、tianxi-api、hkjc-news…） | `wiki/sources/<id>.md` | 只記來源契約，唔貼凍結數字 |
| 賽日回顧 | `wiki/synthesis/race-YYYY-MM-DD.md` | 項目層，會冷 |
| 單場賽事 | **唔開頁** | 結構化賽果留表／chunks |
| 凍結預測、hit-rate、today-picks、模型指紋 | **永不 ingest** | 公開口徑；最多當觀察並記矛盾 |
| 社交草稿／聲線 | `wiki/style/` | 發佈人手批 |
| 工作規則 | `AGENTS.md` `wiki/RULES.md` | 唔入實體頁 |

## 矛盾

- （未有）

## 來源

- [[RULES]]
- [[AGENTS.md]]
