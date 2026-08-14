"""Load and manage Source Registry entries from YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml
from pydantic import ValidationError

from ingestion.models import Source


def _validate_one(data: dict, path: Path) -> Source:
    try:
        return Source.model_validate(data)
    except ValidationError as e:
        raise ValueError(f"Invalid source definition in {path}:\n{e}") from e


def load_sources_from_file(path: Path) -> list[Source]:
    """Load one or many Sources from a YAML file (dict or list)."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return []
    if isinstance(data, dict):
        return [_validate_one(data, path)]
    if isinstance(data, list):
        out: list[Source] = []
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(f"Expected mapping at index {i} in {path}")
            out.append(_validate_one(item, path))
        return out
    raise ValueError(f"Expected mapping or list in {path}, got {type(data)}")


def load_source_from_file(path: Path) -> Source:
    """Back-compat: load exactly one Source (first if list)."""
    items = load_sources_from_file(path)
    if not items:
        raise ValueError(f"No sources in {path}")
    return items[0]


def load_sources_from_dir(directory: Path) -> list[Source]:
    """Load all *.yaml / *.yml sources from a directory (non-recursive)."""
    if not directory.exists():
        return []
    sources: list[Source] = []
    paths = sorted(set(list(directory.glob("*.yaml")) + list(directory.glob("*.yml"))))
    for path in paths:
        sources.extend(load_sources_from_file(path))
    return sources


def get_enabled_sources(sources: Iterable[Source]) -> list[Source]:
    return sorted(
        (s for s in sources if s.enabled),
        key=lambda s: (s.priority, s.id),
    )


def find_source_by_id(sources: Iterable[Source], source_id: str) -> Source | None:
    for s in sources:
        if s.id == source_id:
            return s
    return None
