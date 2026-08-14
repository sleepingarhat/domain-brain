"""Load and manage Source Registry entries from YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml
from pydantic import ValidationError

from ingestion.models import Source


def load_source_from_file(path: Path) -> Source:
    """Load a single Source from a YAML file."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}, got {type(data)}")
    try:
        return Source.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"Invalid source definition in {path}:\n{e}") from e


def load_sources_from_dir(directory: Path) -> list[Source]:
    """Load all *.yaml / *.yml sources from a directory (non-recursive)."""
    if not directory.exists():
        return []
    sources: list[Source] = []
    for path in sorted(directory.glob("*.yaml")) + sorted(directory.glob("*.yml")):
        sources.append(load_source_from_file(path))
    return sources


def get_enabled_sources(sources: Iterable[Source]) -> list[Source]:
    """Return only enabled sources, sorted by priority (1 = highest)."""
    return sorted(
        (s for s in sources if s.enabled),
        key=lambda s: (s.priority, s.id),
    )


def find_source_by_id(sources: Iterable[Source], source_id: str) -> Source | None:
    for s in sources:
        if s.id == source_id:
            return s
    return None
