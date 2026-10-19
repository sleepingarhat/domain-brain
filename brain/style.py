"""Style exemplars: split / tag / profile / retrieve / overlap check.

Raw commentator text is for local style learning only — never verbatim repost.
No LLM key required.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from brain.store import ROOT, _tokenize

STYLE_INDEX_DIR = ROOT / "brain" / "index"
# Commit-safe capped exemplars (PUBLIC repo policy) live under wiki/style/
EXEMPLARS_PATH = ROOT / "wiki" / "style" / "exemplars.json"
EXEMPLARS_FULL_PATH = STYLE_INDEX_DIR / "style_exemplars_full.json"
PROFILES_DIR = ROOT / "wiki" / "style" / "profiles"
STYLE_CHUNKS_MARKER = "style"

SITUATIONS = (
    "大熱門",
    "混戰",
    "冷馬有價",
    "新馬或初出",
    "距離或場地轉變",
    "其他",
)

_SITUATION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "大熱門": ("大熱", "熱門", "賠率低", "穩贏", "一面倒", "壓倒性", "一匹馬", "捧場"),
    "混戰": ("混戰", "難分", "難估", "散開", "多匹有機會", "勢均力敵", "唔好睇死"),
    "冷馬有價": ("冷門", "冷馬", "有價", "賠率高", "爆冷", "伏位", "冷橋", "拾冷"),
    "新馬或初出": ("新馬", "初出", "首次", "處女", "試閘", "未開跑", "新丁"),
    "距離或場地轉變": ("升途", "縮程", "轉場", "轉草地", "轉泥地", "谷草", "沙田轉", "跑馬地轉", "途程"),
}


@dataclass
class Exemplar:
    id: str
    text: str
    commentator: str
    url: str | None
    date: str | None
    situation: str
    source_id: str | None
    score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "commentator": self.commentator,
            "url": self.url,
            "date": self.date,
            "situation": self.situation,
            "source_id": self.source_id,
        }


def split_paragraphs(text: str, *, min_chars: int = 24, max_chars: int = 400) -> list[str]:
    """Split article body into paragraph-level exemplars."""
    if not text or not text.strip():
        return []
    # drop leading "來源: url" lines from web_static chunks
    body = re.sub(r"^來源:\s*\S+\s*\n+", "", text.strip())
    # normalize
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    parts = re.split(r"\n{2,}|(?<=[。！？!?])\s+(?=\S)", body)
    out: list[str] = []
    buf = ""
    for p in parts:
        p = re.sub(r"\s+", " ", p).strip()
        if not p:
            continue
        # skip boilerplate / nav crumbs
        if len(p) < 8:
            continue
        if re.match(r"^(cookie|got it|read more|閱讀更多|分享|訂閱)", p, re.I):
            continue
        candidate = (buf + p).strip() if buf else p
        if len(candidate) < min_chars:
            buf = candidate
            continue
        buf = ""
        if len(candidate) > max_chars:
            # hard-wrap long blocks on sentence boundaries
            sentences = re.split(r"(?<=[。！？!?])", candidate)
            cur = ""
            for s in sentences:
                s = s.strip()
                if not s:
                    continue
                if len(cur) + len(s) <= max_chars:
                    cur += s
                else:
                    if len(cur) >= min_chars:
                        out.append(cur)
                    cur = s
            if len(cur) >= min_chars:
                out.append(cur)
        else:
            out.append(candidate)
    if buf and len(buf) >= min_chars:
        out.append(buf)
    return out


def tag_situation(text: str) -> str:
    """Keyword-rule situation tag. Defaults to 其他."""
    scores: dict[str, int] = {s: 0 for s in SITUATIONS if s != "其他"}
    for situation, kws in _SITUATION_KEYWORDS.items():
        for kw in kws:
            if kw in text:
                scores[situation] += 1
    best = max(scores.items(), key=lambda x: x[1])
    if best[1] <= 0:
        return "其他"
    return best[0]


_PARTICLES = (
    "嘅", "喺", "咗", "喎", "啦", "咋", "咩", "呢", "呀", "喔", "噃", "嘞",
    "唔", "冇", "係", "就", "都", "仲", "先", "再", "睇", "覺得", "估", "相信",
)


def build_style_profile(texts: list[str], commentator: str) -> dict[str, Any]:
    """Purely statistical / lexical profile — no LLM."""
    if not texts:
        return {
            "commentator": commentator,
            "paragraph_count": 0,
            "avg_chars": 0.0,
            "avg_sentences": 0.0,
            "top_particles": [],
            "top_bigrams": [],
            "sample_openers": [],
        }
    lengths = [len(t) for t in texts]
    sent_counts = [max(1, len(re.findall(r"[。！？!?]", t)) or 1) for t in texts]
    particle_counts: Counter[str] = Counter()
    bigrams: Counter[str] = Counter()
    openers: list[str] = []
    for t in texts:
        for p in _PARTICLES:
            c = t.count(p)
            if c:
                particle_counts[p] += c
        toks = _tokenize(t)
        for i in range(len(toks) - 1):
            if len(toks[i]) >= 1 and len(toks[i + 1]) >= 1:
                bigrams[toks[i] + toks[i + 1]] += 1
        opener = t[:18].strip()
        if opener and opener not in openers:
            openers.append(opener)
    return {
        "commentator": commentator,
        "paragraph_count": len(texts),
        "avg_chars": round(sum(lengths) / len(lengths), 1),
        "avg_sentences": round(sum(sent_counts) / len(sent_counts), 2),
        "top_particles": [{"token": t, "count": n} for t, n in particle_counts.most_common(12)],
        "top_bigrams": [{"token": t, "count": n} for t, n in bigrams.most_common(15)],
        "sample_openers": openers[:8],
    }


def profile_to_markdown(profile: dict[str, Any]) -> str:
    cid = profile.get("commentator") or "unknown"
    lines = [
        "---",
        "type: style",
        f"id: style-profile-{cid}",
        f"title: 風格檔案 · {cid}",
        "aliases: []",
        f"sources: [{cid}]",
        "updated: auto",
        "status: active",
        "layer: knowledge",
        "---",
        "",
        f"# 風格檔案 · {cid}",
        "",
        "純統計／詞彙摘要，唔係 LLM 生成。用嚟模仿節奏同語氣，**禁止 verbatim 轉貼原文**。",
        "",
        "## 統計",
        "",
        f"- 段數：{profile.get('paragraph_count', 0)}",
        f"- 平均字數：{profile.get('avg_chars', 0)}",
        f"- 平均句數／段：{profile.get('avg_sentences', 0)}",
        "",
        "## 常用語氣詞／口語",
        "",
    ]
    parts = profile.get("top_particles") or []
    if parts:
        lines.append(", ".join(f"{p['token']}({p['count']})" for p in parts))
    else:
        lines.append("（未夠樣本）")
    lines += ["", "## 常見 bigram", ""]
    bigs = profile.get("top_bigrams") or []
    if bigs:
        lines.append(", ".join(f"{b['token']}({b['count']})" for b in bigs[:10]))
    else:
        lines.append("（未夠樣本）")
    lines += ["", "## 開場樣本（截斷）", ""]
    for o in profile.get("sample_openers") or []:
        lines.append(f"- `{o}…`")
    lines.append("")
    return "\n".join(lines)


def _is_style_chunk(ch: dict[str, Any]) -> bool:
    meta = ch.get("metadata") or {}
    if meta.get("kind") in ("style", "style_exemplar", "style_article"):
        return True
    if meta.get("purpose") == "style":
        return True
    tags = meta.get("domain_tags") or ch.get("domain_tags") or []
    if isinstance(tags, list) and STYLE_CHUNKS_MARKER in tags:
        return True
    sid = str(ch.get("source_id") or "")
    if sid.startswith("style-") or sid.startswith("commentator-"):
        return True
    return False


def load_style_chunks(chunks_dir: Path | None = None) -> list[dict[str, Any]]:
    from brain.store import load_all_chunks

    return [c for c in load_all_chunks(chunks_dir) if _is_style_chunk(c)]


def build_exemplars(
    chunks: list[dict[str, Any]] | None = None,
    *,
    out_path: Path | None = None,
    write_profiles: bool = True,
) -> dict[str, Any]:
    """Build paragraph exemplars + optional wiki style profiles."""
    chunks = chunks if chunks is not None else load_style_chunks()
    exemplars: list[dict[str, Any]] = []
    by_commentator: dict[str, list[str]] = {}

    for ch in chunks:
        meta = ch.get("metadata") or {}
        commentator = (
            meta.get("commentator")
            or meta.get("commentator_id")
            or ch.get("source_id")
            or "unknown"
        )
        url = meta.get("url")
        date = meta.get("date") or meta.get("published") or ch.get("race_date")
        paras = split_paragraphs(ch.get("content") or "")
        for i, para in enumerate(paras):
            sit = tag_situation(para)
            eid = f"{ch.get('id', 'chunk')}:p{i}"
            exemplars.append(
                {
                    "id": eid,
                    "text": para,
                    "commentator": str(commentator),
                    "url": url,
                    "date": date,
                    "situation": sit,
                    "source_id": ch.get("source_id"),
                    "content_hash": ch.get("content_hash"),
                }
            )
            by_commentator.setdefault(str(commentator), []).append(para)

    path = out_path or EXEMPLARS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "count": len(exemplars),
        "situations": list(SITUATIONS),
        "exemplars": exemplars,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    profiles: dict[str, Any] = {}
    if write_profiles:
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        for cid, texts in by_commentator.items():
            profiles[cid] = build_style_profile(texts, cid)
            md = profile_to_markdown(profiles[cid])
            (PROFILES_DIR / f"{cid}.md").write_text(md, encoding="utf-8")

    return {
        "exemplar_count": len(exemplars),
        "commentator_count": len(by_commentator),
        "path": str(path),
        "profiles": list(profiles.keys()),
    }


def load_exemplars(path: Path | None = None) -> list[dict[str, Any]]:
    """Load exemplars. Prefer explicit path; else full local cache, else commit-safe capped."""
    if path is None:
        if EXEMPLARS_FULL_PATH.exists():
            path = EXEMPLARS_FULL_PATH
        else:
            path = EXEMPLARS_PATH
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return list(data.get("exemplars") or [])


def _bm25_rank(query: str, docs: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    tokens_list = [_tokenize(d) for d in docs]
    n = len(tokens_list)
    if n == 0:
        return []
    doc_len = [len(t) for t in tokens_list]
    avgdl = sum(doc_len) / n
    df: dict[str, int] = {}
    for doc in tokens_list:
        for t in set(doc):
            df[t] = df.get(t, 0) + 1
    idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
    q = _tokenize(query)
    scores = [0.0] * n
    for t in q:
        if t not in idf:
            continue
        for i, doc in enumerate(tokens_list):
            freq = doc.count(t)
            if not freq:
                continue
            denom = freq + k1 * (1 - b + b * doc_len[i] / avgdl)
            scores[i] += idf[t] * (freq * (k1 + 1)) / denom
    return scores


def retrieve_exemplars(
    *,
    situation: str | None = None,
    commentator: str | None = None,
    query: str | None = None,
    k: int = 5,
    path: Path | None = None,
) -> list[Exemplar]:
    items = load_exemplars(path)
    if not items:
        return []
    if situation and situation != "全部":
        items = [e for e in items if e.get("situation") == situation]
    if commentator:
        items = [
            e
            for e in items
            if str(e.get("commentator")) == commentator
            or str(e.get("source_id")) == commentator
        ]
    if not items:
        return []

    q = query or (situation or "")
    texts = [str(e.get("text") or "") for e in items]
    scores = _bm25_rank(q, texts) if q else [1.0] * len(items)
    # soft boost exact situation already filtered; prefer longer-ish natural paras
    ranked = sorted(range(len(items)), key=lambda i: scores[i], reverse=True)
    out: list[Exemplar] = []
    for i in ranked[:k]:
        if scores[i] <= 0 and q:
            continue
        e = items[i]
        out.append(
            Exemplar(
                id=str(e.get("id") or i),
                text=str(e.get("text") or ""),
                commentator=str(e.get("commentator") or ""),
                url=e.get("url"),
                date=e.get("date"),
                situation=str(e.get("situation") or "其他"),
                source_id=e.get("source_id"),
                score=round(scores[i], 4),
            )
        )
    # if query filtered everything to zero, fall back to first k unranked
    if not out and items:
        for e in items[:k]:
            out.append(
                Exemplar(
                    id=str(e.get("id")),
                    text=str(e.get("text") or ""),
                    commentator=str(e.get("commentator") or ""),
                    url=e.get("url"),
                    date=e.get("date"),
                    situation=str(e.get("situation") or "其他"),
                    source_id=e.get("source_id"),
                    score=0.0,
                )
            )
    return out


def classify_race_situation(picks: list[dict[str, Any]]) -> str:
    """Classify situation from frozen / model picks.

    Rules (first match wins after specialty checks):
    - any top-4 with win odds >= 10 → 冷馬有價
    - favourite pWin >= 0.30 → 大熱門
    - top pWin < 0.18 and close spread among top-3 → 混戰
    - else 其他
    """
    if not picks:
        return "其他"
    ordered = sorted(
        picks,
        key=lambda p: (
            p.get("rank") if p.get("rank") is not None else 999,
            -(float(p.get("pWin") or p.get("p_win") or 0)),
        ),
    )
    top4 = ordered[:4]
    for p in top4:
        odds = p.get("winOdds")
        if odds is None:
            odds = p.get("odds")
        try:
            if odds is not None and float(odds) >= 10:
                return "冷馬有價"
        except (TypeError, ValueError):
            pass

    top = ordered[0]
    try:
        pwin = float(top.get("pWin") or top.get("p_win") or 0)
    except (TypeError, ValueError):
        pwin = 0.0

    if pwin >= 0.30:
        return "大熱門"

    if pwin < 0.18 and len(ordered) >= 3:
        wins = []
        for p in ordered[:3]:
            try:
                wins.append(float(p.get("pWin") or p.get("p_win") or 0))
            except (TypeError, ValueError):
                wins.append(0.0)
        spread = max(wins) - min(wins)
        if spread <= 0.08:
            return "混戰"

    return "其他"


def classify_race_from_frozen(path: Path, race_number: int) -> str:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    races = data.get("races") or []
    for r in races:
        rn = r.get("raceNumber") or r.get("race_no") or r.get("race")
        if int(rn) == int(race_number):
            picks = r.get("picks") or r.get("runners") or []
            # attach odds from nested if present
            return classify_race_situation(list(picks))
    return "其他"


def longest_overlap(a: str, b: str) -> int:
    """Length of longest common contiguous substring (chars)."""
    if not a or not b:
        return 0
    # bound for safety on long texts
    if len(a) > 2000:
        a = a[:2000]
    if len(b) > 4000:
        b = b[:4000]
    best = 0
    la, lb = len(a), len(b)
    # rolling hash-ish via simple DP on shorter vs longer — O(n*m) ok for short commentary
    prev = [0] * (lb + 1)
    for i in range(1, la + 1):
        cur = [0] * (lb + 1)
        ca = a[i - 1]
        for j in range(1, lb + 1):
            if ca == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


def find_overlap_with_exemplars(
    text: str,
    exemplars: list[str] | list[dict[str, Any]] | list[Exemplar],
    *,
    min_chars: int = 12,
) -> list[dict[str, Any]]:
    """Return hits where output shares a contiguous substring >= min_chars with an exemplar."""
    hits: list[dict[str, Any]] = []
    for ex in exemplars:
        if isinstance(ex, Exemplar):
            body = ex.text
            eid = ex.id
        elif isinstance(ex, dict):
            body = str(ex.get("text") or "")
            eid = str(ex.get("id") or "")
        else:
            body = str(ex)
            eid = ""
        n = longest_overlap(text, body)
        if n >= min_chars:
            # extract one overlapping snippet for diagnostics
            snippet = _extract_overlap_snippet(text, body, n)
            hits.append({"exemplar_id": eid, "overlap_chars": n, "snippet": snippet})
    return hits


def _extract_overlap_snippet(a: str, b: str, n: int) -> str:
    """Find one substring of length n that appears in both."""
    if n <= 0:
        return ""
    # scan a for windows present in b
    for i in range(0, max(0, len(a) - n + 1)):
        window = a[i : i + n]
        if window and window in b:
            return window
    return a[:n]


def reject_if_verbatim(
    text: str,
    exemplars: list[str] | list[dict[str, Any]] | list[Exemplar],
    *,
    min_chars: int = 12,
) -> tuple[bool, list[dict[str, Any]]]:
    """Return (ok, hits). ok=False means reject (too much verbatim overlap)."""
    hits = find_overlap_with_exemplars(text, exemplars, min_chars=min_chars)
    return (len(hits) == 0, hits)
