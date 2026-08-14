"""Optional LLM one-line answer grounded on BM25 hits.

Uses any OpenAI-compatible Chat Completions API:
  export OPENAI_API_KEY=...
  export OPENAI_BASE_URL=https://api.openai.com/v1   # or Groq / Together / etc.
  export OPENAI_MODEL=gpt-4o-mini                     # optional

If no key is set, returns None (CLI still shows raw hits).
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from brain.retrieve import Hit


def synthesize_answer(query: str, hits: list[Hit]) -> str | None:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key or not hits:
        return None

    base = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    context_parts = []
    for i, h in enumerate(hits[:5], 1):
        snippet = h.content[:900]
        context_parts.append(f"[{i}] {h.title}\n{snippet}")
    context = "\n\n".join(context_parts)

    system = (
        "你是「天喜腦」助手，只根據提供的檢索片段回答。"
        "用繁體中文，盡量一句到三句，唔好編造片段以外的事實。"
        "若資料不足，直說資料不足。"
    )
    user = f"問題：{query}\n\n檢索片段：\n{context}\n\n請給精簡答覆："

    url = f"{base}/chat/completions"
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    try:
        return str(data["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError) as e:
        raise RuntimeError(f"Unexpected LLM response shape: {data!r}") from e
