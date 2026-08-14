"""Skeleton: push knowledge chunks into a Dify Knowledge Base via API.

Requires env:
  DIFY_API_BASE   e.g. https://api.dify.ai/v1  or your self-hosted base
  DIFY_API_KEY    dataset API key
  DIFY_DATASET_ID knowledge base / dataset id

This is intentionally minimal — wire into CLI or GHA after you create the dataset.
"""

from __future__ import annotations

import os
from typing import Any

import httpx


def push_text_document(
    name: str,
    text: str,
    *,
    api_base: str | None = None,
    api_key: str | None = None,
    dataset_id: str | None = None,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Create a document-by-text in a Dify dataset.

    See Dify Knowledge API: Create Document by Text.
    """
    api_base = (api_base or os.environ.get("DIFY_API_BASE", "")).rstrip("/")
    api_key = api_key or os.environ.get("DIFY_API_KEY", "")
    dataset_id = dataset_id or os.environ.get("DIFY_DATASET_ID", "")

    if not api_base or not api_key or not dataset_id:
        raise ValueError(
            "Missing DIFY_API_BASE / DIFY_API_KEY / DIFY_DATASET_ID "
            "(env or arguments)"
        )

    url = f"{api_base}/datasets/{dataset_id}/document/create-by-text"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "name": name,
        "text": text,
        "indexing_technique": "high_quality",
        "process_rule": {"mode": "automatic"},
    }

    own_client = client is None
    client = client or httpx.Client(timeout=60.0)
    try:
        resp = client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()
    finally:
        if own_client:
            client.close()


def push_chunks(
    chunks: list[dict[str, Any]],
    *,
    name_prefix: str = "domain-brain",
) -> list[dict[str, Any]]:
    """Push a list of ingestion chunks as separate Dify documents."""
    results = []
    for i, ch in enumerate(chunks):
        title = ch.get("title") or f"{name_prefix}-{i}"
        content = ch.get("content") or ""
        if not content.strip():
            continue
        results.append(push_text_document(str(title), content))
    return results
