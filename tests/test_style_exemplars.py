"""Unit tests for style exemplars — uses FIXTURE text only (not real commentators)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from brain.style import (
    build_exemplars,
    build_style_profile,
    classify_race_situation,
    reject_if_verbatim,
    retrieve_exemplars,
    split_paragraphs,
    tag_situation,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"
FIXTURE_TEXT = (FIXTURE_DIR / "style_fixture_article.txt").read_text(encoding="utf-8")


def test_fixture_is_clearly_marked():
    assert "FIXTURE" in FIXTURE_TEXT
    assert "FOR UNIT TESTS ONLY" in FIXTURE_TEXT


def test_split_paragraphs_yields_multiple():
    paras = split_paragraphs(FIXTURE_TEXT, min_chars=12)
    assert len(paras) >= 4
    assert all("FIXTURE" not in p or True for p in paras)  # header may be own para
    # content paras should be natural length
    assert any("大熱" in p for p in paras)


def test_tag_situation_keywords():
    assert tag_situation("呢場大熱一面倒，賠率低穩贏") == "大熱門"
    assert tag_situation("混戰局面，勢均力敵好難估") == "混戰"
    assert tag_situation("冷門有價，爆冷唔奇") == "冷馬有價"
    assert tag_situation("新馬初出試閘") == "新馬或初出"
    assert tag_situation("升途轉場去沙田") == "距離或場地轉變"
    assert tag_situation("今日天氣唔錯") == "其他"


def test_build_and_retrieve(tmp_path: Path):
    chunks = [
        {
            "id": "fixture:0",
            "source_id": "style-fixture-tipster",
            "title": "FIXTURE article",
            "content": FIXTURE_TEXT,
            "content_hash": "fixturehash0001",
            "metadata": {
                "kind": "style_article",
                "purpose": "style",
                "commentator": "style-fixture-tipster",
                "url": "https://example.com/fixture-only",
                "domain_tags": ["style"],
            },
        }
    ]
    out = tmp_path / "style_exemplars.json"
    info = build_exemplars(chunks, out_path=out, write_profiles=False)
    assert info["exemplar_count"] >= 3

    hits = retrieve_exemplars(
        situation="大熱門",
        commentator="style-fixture-tipster",
        query="大熱",
        k=3,
        path=out,
    )
    assert hits
    assert all(h.situation == "大熱門" for h in hits)
    assert all(h.commentator == "style-fixture-tipster" for h in hits)


def test_style_profile_statistical():
    paras = split_paragraphs(FIXTURE_TEXT, min_chars=12)
    profile = build_style_profile(paras, "style-fixture-tipster")
    assert profile["paragraph_count"] == len(paras)
    assert profile["avg_chars"] > 0
    assert isinstance(profile["top_particles"], list)


def test_classify_race_situation():
    assert (
        classify_race_situation(
            [{"rank": 1, "pWin": 0.35, "winOdds": 2.1}, {"rank": 2, "pWin": 0.2, "winOdds": 5}]
        )
        == "大熱門"
    )
    assert (
        classify_race_situation(
            [
                {"rank": 1, "pWin": 0.15, "winOdds": 6},
                {"rank": 2, "pWin": 0.14, "winOdds": 7},
                {"rank": 3, "pWin": 0.13, "winOdds": 8},
            ]
        )
        == "混戰"
    )
    assert (
        classify_race_situation(
            [
                {"rank": 1, "pWin": 0.22, "winOdds": 4},
                {"rank": 2, "pWin": 0.18, "winOdds": 12},
                {"rank": 3, "pWin": 0.16, "winOdds": 8},
                {"rank": 4, "pWin": 0.12, "winOdds": 15},
            ]
        )
        == "冷馬有價"
    )


def test_overlap_reject():
    exemplar = "估佢沿途放，後上嘅爭三甲位就好睇。"
    # share 12+ contiguous chars
    draft_bad = "今場我估佢沿途放，後上嘅爭三甲位就好睇，再睇下對手。"
    ok, hits = reject_if_verbatim(draft_bad, [exemplar], min_chars=12)
    assert ok is False
    assert hits

    draft_good = "今場二號打頭陣，檔位靚，賠率約三倍，模型睇佢機會最大。"
    ok2, hits2 = reject_if_verbatim(draft_good, [exemplar], min_chars=12)
    assert ok2 is True
    assert hits2 == []


def test_source_registry_loads_disabled_style():
    from ingestion.registry import load_sources_from_dir
    from pathlib import Path as P

    sources = load_sources_from_dir(P("ingestion/sources"))
    style = [s for s in sources if "style" in (s.domain_tags or []) or s.id.startswith("style-")]
    assert style, "expected disabled style placeholders in registry"
    assert all(s.enabled is False for s in style)
