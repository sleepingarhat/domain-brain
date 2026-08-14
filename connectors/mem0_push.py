"""Push reflection notes / facts into Mem0 Platform for 天喜腦 (TianxiBrain).

Requires:
  pip install mem0ai
  export MEM0_API_KEY=...
  optional: MEM0_USER_ID=tianxi-brain
"""

from __future__ import annotations

import os
from typing import Any


def get_client(api_key: str | None = None):
    try:
        from mem0 import MemoryClient
    except ImportError as e:
        raise ImportError(
            "mem0ai not installed. Run: pip install mem0ai"
        ) from e

    key = api_key or os.environ.get("MEM0_API_KEY", "")
    if not key:
        raise ValueError("MEM0_API_KEY is required")
    return MemoryClient(api_key=key)


def add_text_memory(
    text: str,
    *,
    user_id: str | None = None,
    metadata: dict[str, Any] | None = None,
    api_key: str | None = None,
) -> Any:
    """Store a free-form text memory (assistant message style)."""
    client = get_client(api_key)
    uid = user_id or os.environ.get("MEM0_USER_ID", "tianxi-brain")
    messages = [{"role": "assistant", "content": text}]
    return client.add(messages, user_id=uid, metadata=metadata or {})


def add_reflection_note(
    note: dict[str, Any],
    *,
    user_id: str | None = None,
    api_key: str | None = None,
) -> Any:
    """Store a race reflection note from agents.reflection_agent."""
    from agents.reflection_agent import reflection_to_mem0_payload

    uid = user_id or os.environ.get("MEM0_USER_ID", "tianxi-brain")
    payload = reflection_to_mem0_payload(note, user_id=uid)
    client = get_client(api_key)
    return client.add(
        payload["messages"],
        user_id=payload["user_id"],
        metadata=payload.get("metadata") or {},
    )


def search_memories(
    query: str,
    *,
    user_id: str | None = None,
    api_key: str | None = None,
    limit: int = 5,
) -> Any:
    client = get_client(api_key)
    uid = user_id or os.environ.get("MEM0_USER_ID", "tianxi-brain")
    return client.search(query, user_id=uid, limit=limit)
