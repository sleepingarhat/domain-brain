# Dify / Mem0 註冊與接駁指南

你先自己註冊，**唔使把 API key 傳俾任何人**。只係喺本機或 GitHub Secrets 設環境變數。

---

## 1. Dify（知識庫 / RAG）

### 註冊

- **Cloud（最快）**: https://cloud.dify.ai  
  可用 GitHub / Google / 電郵註冊，Sandbox 可免費試。
- 文件: https://docs.dify.ai
- API base（Cloud）: `https://api.dify.ai/v1`

### 你要準備嘅三樣

1. **Knowledge API Key**  
   喺 Dify 控制台 → 知識庫 / API 相關設定建立（用於管理 dataset）
2. **Dataset ID**  
   新建一個 Knowledge Base（建議名：`ma-shen` 或 `domain-brain-horse`），複製其 ID
3. **API Base**  
   Cloud 用 `https://api.dify.ai/v1`；自建就用你自己嘅網址 + `/v1`

### 本機環境變數

```bash
export DIFY_API_BASE="https://api.dify.ai/v1"
export DIFY_API_KEY="你的-knowledge-api-key"
export DIFY_DATASET_ID="你的-dataset-id"
```

程式入口：`connectors/dify_push.py`

---

## 2. Mem0（長期記憶）

### 註冊

- **Platform**: https://app.mem0.ai  
  註冊後到 Dashboard → API Keys 建立 key
- 文件: https://docs.mem0.ai/platform/quickstart
- 開源自建亦可: https://github.com/mem0ai/mem0

### 你要準備

1. **MEM0_API_KEY**

```bash
export MEM0_API_KEY="你的-mem0-api-key"
export MEM0_USER_ID="ma-shen"   # 可選，預設 ma-shen
```

程式入口：`connectors/mem0_push.py`

---

## 3. 建議註冊順序

1. 先開 **Dify Cloud**，建一個空 Knowledge Base（馬神）
2. 再開 **Mem0**，拎 API key
3. 本機設好環境變數
4. 回報我「Dify dataset 已建好 / Mem0 key 已備好」（**唔使貼 key**），我再幫你接 CLI 一鍵推送同賽後反思寫入

---

## 4. 安全

- API key 只放本機 `.env` 或 GitHub Actions Secrets
- **唔好** commit 入 git
- **唔好**貼喺聊天
