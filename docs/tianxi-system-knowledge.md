# 天喜系統知識層（tianxi-repos）

令天喜腦識答「天喜引擎點運作、網站有咩、Pro 有咩唔同」，同埋為介紹／宣傳／Q&A 帖提供有出處嘅事實。

## 頁面

`wiki/concepts/tianxi/`（type: concept）：

| 頁 | 內容 |
|---|---|
| `天喜引擎.md` | ELO＋LightGBM、因子、T−90 凍結、初版／最終版、自動修復、健康閘、回測、模型帳本（`status: observation`） |
| `系統架構.md` | 資料層／訓練回測層／服務層、每日排程、公開 API |
| `開發歷程.md` | 有 commit 支持嘅里程碑 |
| `網站功能.md` | 每頁用戶攞到咩 |
| `社群與頻道.md` | Telegram／FB／X／IG／Threads |
| `天喜問答.md` | 社交 Q&A |
| `宣傳要點.md` | 真實賣點＋禁止聲稱 |

來源頁：`wiki/sources/tianxi-repos.md`。

## 規則

- 每條事實要有出處（檔案@commit、commit hash 或公開頁）；唔清楚寫「待確認」。
- 唔寫命中率／ROI 數字、模型指紋、密鑰、env、內部網址、管理端點。
- 社交發佈仍要人手批（AGENTS.md）。

## 自動刷新

`ingestion/sources/tianxi-repos.yaml` → `connectors/github_docs.py`：

- 讀兩個公開倉嘅指定 README／docs（raw.githubusercontent.com）同最近 30 條人手 commit 標題（api.github.com）。
- 含 token／secret／admin／workers.dev 等字眼嘅行會被剔走。
- 只寫內容有變嘅文件（對比現存 chunks 嘅 content_hash）；冇變就 `skipped`。
- `Brain Daily` results slot（01:30 HKT）自動跑；喺 Actions 用 `github.token` 提高 rate limit。
- Compile 唔會改知識頁，只喺 `wiki/sources/tianxi-repos.md` append「文件更新 repo/path @sha」觀察——見到新觀察就要人手覆核對應頁。

## 手動刷新

```bash
python -m ingestion.cli --source tianxi-repos
python -m brain.cli compile
python -m brain.cli build
python -m brain.cli query "天喜引擎 凍結" --layer wiki
```

要加新文件：喺 `tianxi-repos.yaml` 對應 repo 嘅 `paths` 加路徑。更新知識頁：讀新 chunk（`ingestion/chunks/*-tianxi-repos.json`），按 `wiki/RULES.md` 只追加帶日期嘅結論／觀察，衝突寫入「矛盾」。
