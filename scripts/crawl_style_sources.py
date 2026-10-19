#!/usr/bin/env python3
"""Crawl style + knowledge sources into private raw store + commit-safe chunks.

PUBLIC-repo policy:
  - Full article/subtitle text → ingestion/private/raw/ (gitignored)
  - Knowledge chunks (paraphrased/structured facts + source URL + topic tags)
    → ingestion/chunks/ (committable)
  - Style exemplars stored capped ≤200 chars + URL in brain/index/style_exemplars.json
  - Full exemplar paragraphs → brain/index/style_exemplars_full.json (gitignored)
"""

from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_RAW = ROOT / "ingestion" / "private" / "raw"
CHUNKS_DIR = ROOT / "ingestion" / "chunks"
STATE_PATH = ROOT / "ingestion" / "private" / "crawl_state.json"
HK_TZ = timezone(timedelta(hours=8))
UA = (
    "Mozilla/5.0 (compatible; domain-brain-style/0.2; "
    "+https://github.com/sleepingarhat/domain-brain)"
)
DELAY = 2.2
EXCERPT_CAP = 200

# Topic tags for non-race-day knowledge articles
TOPIC_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("馬匹生理與獸醫", ("喘鳴", "氣管", "流鼻血", "Tie-back", "獸醫", "筋腱", "關節", "步態")),
    ("晨操與試閘", ("晨操", "試閘", "沙圈", "操練", "快跳", "拍跳")),
    ("場地與途程", ("沙田", "跑馬地", "草地", "泥地", "全天候", "途程", "升途", "縮程", "C+3", "檔位")),
    ("檔位與冷熱偏", ("檔位", "內檔", "外檔", "大熱", "冷門", "冷熱", "賠率")),
    ("班次與評分", ("班次", "評分", "讓磅", "負磅", "升班", "落班", "第四班", "第五班")),
    ("閱讀賽績", ("近績", "程績", "同場同程", "走位", "放頭", "跟前", "後上", "收腳", "鬥腳")),
    ("投注池基礎", ("獨贏", "位置", "連贏", "三重彩", "過關", "值博", "派彩", "注碼")),
    ("騎師練馬師", ("騎師", "練馬師", "馬房", "配搭")),
]


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _load_state() -> dict[str, Any]:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"seen_urls": {}}


def _save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


class Crawler:
    def __init__(self) -> None:
        self.client = httpx.Client(timeout=35.0, follow_redirects=True, headers={"User-Agent": UA})
        self.robots: dict[str, RobotFileParser] = {}
        self.state = _load_state()
        self.stats: dict[str, Any] = {}

    def allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self.robots:
            rp = RobotFileParser()
            try:
                resp = self.client.get(urljoin(origin, "/robots.txt"))
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                else:
                    rp.parse([])
            except Exception:
                rp.parse([])
            self.robots[origin] = rp
            time.sleep(0.3)
        try:
            return bool(self.robots[origin].can_fetch(UA, url))
        except Exception:
            return True

    def fetch(self, url: str) -> tuple[int, str, str]:
        """Return status, html, decoded_text_hint."""
        if not self.allowed(url):
            return 0, "", "robots-disallow"
        time.sleep(DELAY)
        resp = self.client.get(url)
        if resp.status_code in (401, 402, 403):
            return resp.status_code, "", "paywall"
        raw = resp.content
        text = raw.decode("utf-8", "ignore")
        if "racing.on.cc" in url or ("charset=Big5" in text[:500] or "charset=big5" in text[:500]):
            try:
                text = raw.decode("big5", "ignore")
            except Exception:
                pass
        return resp.status_code, text, "ok"

    def extract(self, html: str, url: str) -> tuple[str, str | None]:
        try:
            import trafilatura

            body = trafilatura.extract(
                html, include_comments=False, include_tables=False, favor_recall=True, url=url
            ) or ""
            meta = trafilatura.extract_metadata(html)
            title = getattr(meta, "title", None) if meta else None
            if len(body) >= 80:
                return body.strip(), title
        except Exception:
            pass
        from connectors.web_static import _html_to_text

        return _html_to_text(html), None

    def save_raw(self, source_id: str, url: str, title: str, body: str, meta: dict) -> Path:
        PRIVATE_RAW.mkdir(parents=True, exist_ok=True)
        h = _hash(url)
        path = PRIVATE_RAW / f"{source_id}-{h}.json"
        path.write_text(
            json.dumps(
                {
                    "source_id": source_id,
                    "url": url,
                    "title": title,
                    "content": body,
                    "content_hash": _hash(body),
                    "fetched_at": datetime.now(HK_TZ).isoformat(),
                    "metadata": meta,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return path

    def seen(self, url: str) -> bool:
        return url in (self.state.get("seen_urls") or {})

    def mark(self, url: str, info: dict) -> None:
        self.state.setdefault("seen_urls", {})[url] = info


def tag_topics(text: str) -> list[str]:
    hits = []
    for topic, kws in TOPIC_RULES:
        if any(k in text for k in kws):
            hits.append(topic)
    return hits or ["綜合"]


def paraphrase_knowledge(title: str, body: str, url: str, source_id: str) -> dict[str, Any]:
    """Structured knowledge chunk — short factual notes, not verbatim dump."""
    # take up to 6 informative sentences, compress to notes
    sentences = re.split(r"(?<=[。！？!?；;])", body)
    notes: list[str] = []
    for s in sentences:
        s = re.sub(r"\s+", " ", s).strip()
        if len(s) < 12 or len(s) > 120:
            continue
        # skip pure tip lists / odds spam
        if s.count("號") > 4 and ("連贏" in s or "過關" in s):
            continue
        notes.append(s)
        if len(notes) >= 6:
            break
    topics = tag_topics(title + "\n" + body)
    summary = "；".join(notes[:4]) if notes else title
    # ensure not huge
    summary = summary[:500]
    content = (
        f"【知識摘要·非原文】來源: {url}\n"
        f"標題: {title}\n"
        f"主題標籤: {', '.join(topics)}\n"
        f"要點: {summary}"
    )
    return {
        "source_id": source_id,
        "title": f"[知識] {title}"[:120],
        "content": content,
        "content_hash": _hash(content),
        "metadata": {
            "kind": "knowledge",
            "purpose": "knowledge",
            "url": url,
            "domain_tags": ["knowledge", "commentary", *topics],
            "topics": topics,
            "paraphrased": True,
        },
    }


def style_chunk_meta(source_id: str, commentator: str, url: str, title: str) -> dict:
    return {
        "kind": "style_article",
        "purpose": "style",
        "commentator": commentator,
        "url": url,
        "title": title,
        "domain_tags": ["style", "commentary", "cantonese"],
    }


def crawl_horsetrio(c: Crawler, max_articles: int = 150) -> list[dict]:
    source_id = "style-horsetrio"
    commentator = "horsetrio"
    articles: list[dict] = []
    # sitemap
    st, html, _ = c.fetch("https://horsetrio.com/sitemap.xml")
    urls = re.findall(r"<loc>(https://horsetrio.com/[^<]+)</loc>", html)
    # prefer race analyses + learn/study
    prefer = []
    for u in urls:
        if re.search(r"/posts/MTG_.+/r/\d+$", u):
            prefer.append(u)
        elif re.search(r"/posts/MTG_.+/(report|review)$", u):
            prefer.append(u)
        elif "/learn/" in u or "/study/" in u:
            prefer.append(u)
    # dedupe keep order
    seen = set()
    ordered = []
    for u in prefer:
        if u not in seen:
            seen.add(u)
            ordered.append(u)
    ordered = ordered[:max_articles]
    print(f"[horsetrio] candidate urls: {len(ordered)}")
    for url in ordered:
        if c.seen(url):
            continue
        st, html, hint = c.fetch(url)
        if st != 200 or hint in ("robots-disallow", "paywall"):
            c.mark(url, {"status": st, "hint": hint})
            continue
        body, title = c.extract(html, url)
        if len(body) < 200 or "歷史文章" in body[:80] and len(body) < 400:
            c.mark(url, {"status": "thin"})
            continue
        title = title or url.rstrip("/").split("/")[-1]
        c.save_raw(source_id, url, title, body, {"commentator": commentator})
        articles.append({"url": url, "title": title, "body": body, "source_id": source_id, "commentator": commentator})
        c.mark(url, {"status": "ok", "chars": len(body)})
        print(f"  + {title[:40]} ({len(body)} chars)")
    c.stats["horsetrio"] = len(articles)
    return articles


def crawl_hkdn(c: Crawler, max_articles: int = 80) -> list[dict]:
    source_id = "style-hkdn-racing"
    commentator = "hkdn-教父"
    articles: list[dict] = []
    listing = "https://hkdnracing.com/zh/news"
    st, html, hint = c.fetch(listing)
    if st != 200:
        print("[hkdn] listing failed", st, hint)
        return articles
    hrefs = sorted(set(re.findall(r'href="(/zh/news/[^"]+)"', html)))
    # also homepage
    st2, html2, _ = c.fetch("https://hkdnracing.com/zh")
    hrefs += re.findall(r'href="(/zh/news/[^"]+)"', html2)
    hrefs = sorted(set(hrefs))[:max_articles]
    print(f"[hkdn] news urls: {len(hrefs)}")
    for href in hrefs:
        url = "https://hkdnracing.com" + href
        if c.seen(url):
            continue
        st, html, hint = c.fetch(url)
        if st != 200 or hint in ("robots-disallow", "paywall"):
            c.mark(url, {"status": st, "hint": hint})
            continue
        body, title = c.extract(html, url)
        if len(body) < 80:
            c.mark(url, {"status": "thin"})
            continue
        title = title or href.split("/")[-1]
        c.save_raw(source_id, url, title, body, {"commentator": commentator})
        articles.append({"url": url, "title": title, "body": body, "source_id": source_id, "commentator": commentator})
        c.mark(url, {"status": "ok", "chars": len(body)})
        print(f"  + {title[:40]} ({len(body)})")
    c.stats["hkdn"] = len(articles)
    return articles


def crawl_oncc(c: Crawler, max_articles: int = 40) -> list[dict]:
    """東網馬經 — current morning/fav pages (archive deep-links limited)."""
    source_id = "style-oncc-racing"
    commentator = "oncc-馬經"
    seeds = [
        "https://racing.on.cc/",
        "https://racing.on.cc/racing/mor/current/rjmora0001x0.html",
        "https://racing.on.cc/racing/mor/current/rjmorb0001x0.html",
        "https://racing.on.cc/racing/mor/current/rjmorc0001x0.html",
        "https://racing.on.cc/racing/fav/current/rjfavg0001x0.html",
        "https://racing.on.cc/racing/fav/current/rjfavf0101x0.html",
        "https://racing.on.cc/racing/fav/current/rjfavf0201x0.html",
        "https://racing.on.cc/racing/fav/current/rjfavf0301x0.html",
    ]
    articles: list[dict] = []
    print(f"[oncc] seeds: {len(seeds)}")
    for url in seeds[:max_articles]:
        if c.seen(url):
            continue
        st, html, hint = c.fetch(url)
        if st != 200 or hint in ("robots-disallow", "paywall"):
            c.mark(url, {"status": st, "hint": hint})
            print(f"  skip {url} {st} {hint}")
            continue
        body, title = c.extract(html, url)
        if len(body) < 100:
            c.mark(url, {"status": "thin"})
            continue
        title = title or f"on.cc {url.split('/')[-1]}"
        c.save_raw(source_id, url, title, body, {"commentator": commentator})
        articles.append({"url": url, "title": title, "body": body, "source_id": source_id, "commentator": commentator})
        c.mark(url, {"status": "ok", "chars": len(body)})
        print(f"  + {title[:40]} ({len(body)})")
    c.stats["oncc"] = len(articles)
    return articles


def crawl_youtube(c: Crawler, channel_id: str, source_id: str, commentator: str, max_videos: int = 20) -> list[dict]:
    import subprocess
    import tempfile

    articles: list[dict] = []
    channel_url = f"https://www.youtube.com/channel/{channel_id}"
    print(f"[youtube:{commentator}] listing {channel_url}")
    try:
        proc = subprocess.run(
            [
                "yt-dlp",
                "--flat-playlist",
                "--dump-json",
                "--playlist-end",
                str(max_videos),
                channel_url + "/videos",
            ],
            capture_output=True,
            text=True,
            timeout=180,
        )
    except Exception as e:
        print("  list failed", e)
        c.stats[source_id] = 0
        return articles
    vids = []
    for line in proc.stdout.splitlines():
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        vid = obj.get("id")
        if vid:
            vids.append((vid, obj.get("title") or vid))
    print(f"  videos listed: {len(vids)}")
    for vid, vtitle in vids[:max_videos]:
        url = f"https://www.youtube.com/watch?v={vid}"
        if c.seen(url):
            continue
        time.sleep(DELAY)
        try:
            with tempfile.TemporaryDirectory(prefix="yt-") as tmp:
                outtmpl = str(Path(tmp) / "%(id)s")
                proc = subprocess.run(
                    [
                        "yt-dlp",
                        "--skip-download",
                        "--write-auto-sub",
                        "--write-sub",
                        "--sub-langs",
                        "zh-HK,yue,zh-Hant,zh-TW,zh",
                        "--sub-format",
                        "vtt",
                        "-o",
                        outtmpl,
                        url,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=180,
                )
                vtts = list(Path(tmp).glob("*.vtt"))
                if not vtts:
                    c.mark(url, {"status": "no-subs"})
                    print(f"  no subs: {vtitle[:40]}")
                    continue
                pref = ("zh-HK", "yue", "zh-Hant", "zh-TW", "zh")

                def rank(p: Path) -> int:
                    name = p.name.lower()
                    for i, lang in enumerate(pref):
                        if lang.lower() in name:
                            return i
                    return 99

                vtts.sort(key=rank)
                raw = vtts[0].read_text(encoding="utf-8", errors="ignore")
                lines = []
                for line in raw.splitlines():
                    line = line.strip()
                    if not line or line.startswith("WEBVTT") or "-->" in line or re.match(r"^\d+$", line):
                        continue
                    line = re.sub(r"<[^>]+>", "", line)
                    if line and (not lines or lines[-1] != line):
                        lines.append(line)
                body = "\n".join(lines).strip()
                if len(body) < 40:
                    c.mark(url, {"status": "thin-subs"})
                    continue
                title = vtitle
                c.save_raw(source_id, url, title, body, {"commentator": commentator, "video_id": vid})
                articles.append(
                    {
                        "url": url,
                        "title": title,
                        "body": body,
                        "source_id": source_id,
                        "commentator": commentator,
                    }
                )
                c.mark(url, {"status": "ok", "chars": len(body)})
                print(f"  + {title[:40]} ({len(body)})")
        except Exception as e:
            c.mark(url, {"status": f"err:{e}"})
            print(f"  err {vid}: {e}")
    c.stats[source_id] = len(articles)
    return articles


def write_outputs(articles: list[dict]) -> dict[str, Any]:
    """Write knowledge chunks + style article stubs into ingestion/chunks."""
    from brain.style import split_paragraphs, tag_situation, build_exemplars

    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(HK_TZ)
    run_id = started.strftime("%Y%m%d-%H%M%S")

    # knowledge chunks (committable)
    knowledge: list[dict] = []
    style_articles: list[dict] = []
    for art in articles:
        knowledge.append(
            paraphrase_knowledge(art["title"], art["body"], art["url"], art["source_id"])
        )
        # style article chunk stores ONLY capped preview in committed file;
        # full text already in private raw. For style-build we point at private.
        preview = art["body"][:EXCERPT_CAP]
        style_articles.append(
            {
                "source_id": art["source_id"],
                "title": art["title"][:120],
                "content": f"來源: {art['url']}\n\n{preview}",
                "content_hash": _hash(art["body"]),
                "metadata": {
                    **style_chunk_meta(art["source_id"], art["commentator"], art["url"], art["title"]),
                    "excerpt_only": True,
                    "full_chars": len(art["body"]),
                },
            }
        )

    kpath = CHUNKS_DIR / f"{run_id}-style-knowledge.json"
    spath = CHUNKS_DIR / f"{run_id}-style-excerpts.json"
    kpath.write_text(json.dumps(knowledge, ensure_ascii=False, indent=2), encoding="utf-8")
    spath.write_text(json.dumps(style_articles, ensure_ascii=False, indent=2), encoding="utf-8")

    # Build FULL exemplars from private raw (for local style-check quality),
    # then write capped commit-safe exemplars.
    full_chunks = []
    for art in articles:
        full_chunks.append(
            {
                "id": f"private:{_hash(art['url'])}",
                "source_id": art["source_id"],
                "title": art["title"],
                "content": art["body"],
                "content_hash": _hash(art["body"]),
                "metadata": style_chunk_meta(
                    art["source_id"], art["commentator"], art["url"], art["title"]
                ),
            }
        )
    full_path = ROOT / "brain" / "index" / "style_exemplars_full.json"
    info_full = build_exemplars(full_chunks, out_path=full_path, write_profiles=True)

    # Cap exemplars for public commit
    full_data = json.loads(full_path.read_text(encoding="utf-8"))
    capped = []
    for ex in full_data.get("exemplars") or []:
        text = str(ex.get("text") or "")
        capped.append(
            {
                **ex,
                "text": text[:EXCERPT_CAP],
                "excerpt_only": True,
                "full_chars": len(text),
            }
        )
    cap_path = ROOT / "wiki" / "style" / "exemplars.json"
    cap_path.parent.mkdir(parents=True, exist_ok=True)
    cap_path.write_text(
        json.dumps(
            {
                "version": 1,
                "count": len(capped),
                "policy": "PUBLIC_REPO_EXCERPT_CAP_200",
                "situations": full_data.get("situations"),
                "exemplars": capped,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    return {
        "articles": len(articles),
        "knowledge_chunks": len(knowledge),
        "style_excerpts": len(style_articles),
        "exemplars_full": info_full.get("exemplar_count"),
        "exemplars_capped": len(capped),
        "knowledge_path": str(kpath),
        "excerpts_path": str(spath),
        "profiles": info_full.get("profiles"),
    }


def main() -> int:
    c = Crawler()
    all_arts: list[dict] = []
    all_arts += crawl_horsetrio(c, max_articles=150)
    all_arts += crawl_hkdn(c, max_articles=80)
    all_arts += crawl_oncc(c, max_articles=40)
    # YouTube channels
    yt = [
        ("UCtsYxC1zCclLuBC8XOxW5zw", "style-youtube-dami", "大米講馬"),
        ("UCrRUvqYlcLl9vETA3tnFIBw", "style-youtube-leung", "梁西華講馬經"),
        ("UCar1cXEurmG5tNsrrYpyq4A", "style-youtube-leimin", "喱民頻道"),  # 喘民→喱民
    ]
    for cid, sid, name in yt:
        all_arts += crawl_youtube(c, cid, sid, name, max_videos=20)

    _save_state(c.state)
    summary = write_outputs(all_arts)
    summary["per_source"] = c.stats
    summary["unique_articles"] = len(all_arts)
    out = ROOT / "logs" / f"crawl_{datetime.now(HK_TZ).strftime('%Y%m%d-%H%M%S')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"log: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
