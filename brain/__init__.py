"""天喜腦（TianxiBrain）— 本地檢索 + wiki 編譯層。

chunks（BM25）負責原文召回；wiki 負責實體記憶演化。
不依賴雲端知識庫付費額度。
"""

__all__ = ["build_index", "search", "compile_chunks"]

from brain.compile import compile_chunks
from brain.retrieve import build_index, search
