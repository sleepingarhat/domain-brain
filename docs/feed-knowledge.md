# 點餵文章／知識入天喜腦

餵完一定要 **build 索引**，查詢先會搵到：

```bash
python -m brain.cli build
python -m brain.cli query "你的問題"
```

---

## 方法 1：自動（已設定）

每日 GitHub Actions 會拉：

- tianxi 賽果／預測
- HKJC、Idol Horse、The Standard（免費公開源）

你唔使每次手動餵呢啲。

---

## 方法 2：餵本地文章（推薦人手內容）

### 單檔

```bash
python -m ingestion.cli --feed-file ./我的分析.md --title "周三夜馬筆記"
python -m brain.cli build
```

### 成個資料夾

把 `.md` / `.txt` 放入 `ingestion/manual/`：

```bash
python -m ingestion.cli --feed-dir ingestion/manual
python -m brain.cli build
```

---

## 方法 3：餵一條公開文章 URL

```bash
python -m ingestion.cli --feed-url "https://idolhorse.com/某篇文章/" --title "Idol Horse 專題"
python -m brain.cli build
```

只適合 **公開、唔使登入** 嘅頁。付費牆會失敗。

---

## 方法 4：跑已註冊來源

```bash
python -m ingestion.cli --list
python -m ingestion.cli --source idol-horse
python -m ingestion.cli --source hkjc-news
python -m brain.cli build
```

---

## 流程圖

```text
文章 / URL / 自動源
        ↓
ingestion.cli（寫入 chunks）
        ↓
brain.cli build（BM25 索引）
        ↓
brain.cli query
```
