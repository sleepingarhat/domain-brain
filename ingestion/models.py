"""Core data models for Knowledge Ingestion Layer."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class SourceType(str, Enum):
    WEB_CRAWL = "web_crawl"
    RSS = "rss"
    API = "api"
    DATABASE = "database"
    MANUAL = "manual"


class RunStatus(str, Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    SKIPPED = "skipped"


class Source(BaseModel):
    """A single entry in the Source Registry."""

    id: str = Field(..., pattern=r"^[a-z0-9][a-z0-9\-_]{1,63}$")
    name: str = Field(..., min_length=1, max_length=120)
    type: SourceType
    enabled: bool = True
    url: str | None = None
    schedule: str | None = None
    domain_tags: list[str] = Field(default_factory=list)
    priority: int = Field(default=5, ge=1, le=10)
    auth: dict[str, Any] | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    notes: str | None = None


class CrawlRun(BaseModel):
    """Record of one execution of a knowledge source."""

    run_id: str
    source_id: str
    started_at: datetime
    finished_at: datetime | None = None
    status: RunStatus
    items_fetched: int = 0
    items_new: int = 0
    items_updated: int = 0
    items_skipped: int = 0
    error_message: str | None = None
    duration_seconds: float | None = None
    content_hash: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class HealthMetrics(BaseModel):
    """Aggregated health for a source (derived from recent runs)."""

    source_id: str
    success_rate_7d: float | None = None
    success_rate_30d: float | None = None
    consecutive_failures: int = 0
    last_success_at: datetime | None = None
    last_run_at: datetime | None = None
    avg_items_new: float | None = None
    avg_duration_seconds: float | None = None
    updated_at: datetime | None = None
