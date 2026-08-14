"""天喜腦（TianxiBrain）— 輕量開源本地檢索層（方案 B）。

不依賴 Dify Cloud credits。以 ingestion chunks 建 BM25 索引，支援 CLI 查詢。
"""

__all__ = ["build_index", "search"]

from brain.retrieve import build_index, search
