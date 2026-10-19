# 風格 Exemplars（模仿評馬人聲線）

用嚟學粵語評馬人嘅語氣同節奏，**唔係** verbatim 轉載專欄。  
原文只留喺本機／倉內做風格學習；對外發文一定要改寫，並過 `style-check`。

## 一覽

```text
Source Registry（style-*）
        ↓  crawl（trafilatura / yt-dlp / manual）
ingestion/chunks/*.json   metadata.kind=style_article
        ↓  python -m brain.cli style-build
brain/index/style_exemplars.json   + wiki/style/profiles/<id>.md
        ↓  python -m brain.cli style --situation …
賽前評述 prompt（prompts/07-style-commentary.md）
        ↓  style-check（禁 ≥12 字原文重疊）
人手批發佈
```

## 點樣加一個評馬人

1. 喺 `ingestion/sources/style-commentators.yaml` 加一條（可抄 `examples/sources/style-commentator.example.yaml`）。
2. 必填：

| 欄位 | 說明 |
|------|------|
| `id` | 例如 `style-wong-siu-ming`（小寫、連字） |
| `name` | 顯示名 |
| `type` | `web_crawl` / `youtube` / `manual`（`rss` 預留） |
| `enabled` | 確認公開可讀、無付費牆先改 `true` |
| `schedule` | cron（可選；GHA 每週一亦會掃全部 enabled） |
| `domain_tags` | **一定要有** `style` |
| `config.purpose` | `style` |
| `config.commentator` | 穩定 id，檢索用 |
| `config.listing_urls` / `seed_urls` / `article_urls` | 網頁 |
| `config.channel_url` / `video_urls` | YouTube |
| `config.max_items` | 每次最多篇／條 |
| `config.delay_seconds` | 礼貌間隔（預設 2s） |
| `config.respect_robots` | 預設 true |

3. 安裝可選依賴：`pip install -e ".[style]"`（trafilatura、yt-dlp）。
4. 跑：

```bash
python -m ingestion.cli --source style-wong-siu-ming
python -m brain.cli style-build
python -m brain.cli style --situation 大熱門 --commentator style-wong-siu-ming --k 5
```

5. 賽前自動判斷形勢（由凍結 picks）：

```bash
python -m brain.cli style --from-frozen /path/to/frozen.json --race 5 --k 5
```

規則：頂四有獨贏 ≥10 → `冷馬有價`；頭馬 pWin≥0.30 → `大熱門`；頭馬 pWin<0.18 且前三接近 → `混戰`；其餘 `其他`。段落亦會用關鍵詞 tag：`新馬或初出`／`距離或場地轉變` 等。

## 形勢標籤

`大熱門` · `混戰` · `冷馬有價` · `新馬或初出` · `距離或場地轉變` · `其他`

## 寫評述

跟 `prompts/07-style-commentary.md`：模仿 exemplars 聲線，內容只用凍結 + 腦庫事實；寫完：

```bash
python -m brain.cli style-check --text '你嘅草稿…' --situation 大熱門 --k 20
```

`ok: false` 就要改到冇 ≥12 字連續相同。

## GitHub Actions

`.github/workflows/04-crawl-style-exemplars.yml`：每週一 + 手動。  
**而家所有 style source 都係 `enabled: false`，跑咗都係 no-op。** Owner 交齊 URL 再開。

## 版權

- 唔過 paywall、唔用登入 cookie
- 尊重 robots.txt
- 倉內原文只供風格學習；對外帖文禁止大段照抄


## PUBLIC 倉版權政策

`sleepingarhat/domain-brain` 若係 **PUBLIC**：全文只存 `ingestion/private/`（gitignore）；git 只收知識摘要 chunk、`wiki/style/exemplars.json`（每段 ≤200 字 + URL）、同 `wiki/style/profiles/`。
排程用本機 `scripts/style_refresh.sh`，唔好喺 Actions commit 原文。
