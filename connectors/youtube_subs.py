"""Fetch YouTube auto-subtitles (zh-HK / yue / zh-Hant) via yt-dlp for style learning.

Requires: pip install yt-dlp  (or pip install -e ".[style]")
Does not download video — subtitles / auto-subs only.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from ingestion.models import CrawlRun, RunStatus, Source

HK_TZ = timezone(timedelta(hours=8))
PREF_LANGS = ("zh-HK", "yue", "zh-Hant", "zh-TW", "zh", "en")


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _vtt_to_text(vtt: str) -> str:
    lines: list[str] = []
    for line in vtt.splitlines():
        line = line.strip()
        if not line or line.startswith("WEBVTT") or line.startswith("NOTE"):
            continue
        if re.match(r"^\d+$", line):
            continue
        if "-->" in line:
            continue
        # strip simple tags
        line = re.sub(r"<[^>]+>", "", line)
        if line and (not lines or lines[-1] != line):
            lines.append(line)
    return "\n".join(lines).strip()


def _ytdlp_available() -> bool:
    try:
        subprocess.run(
            ["yt-dlp", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


class YoutubeSubsConnector:
    def __init__(self, source: Source):
        self.source = source
        cfg = source.config or {}
        self.urls: list[str] = list(
            cfg.get("video_urls")
            or cfg.get("seed_urls")
            or ([source.url] if source.url else [])
        )
        # channel / playlist URL harvested lightly via yt-dlp flat playlist
        self.channel_url = cfg.get("channel_url") or cfg.get("playlist_url")
        self.max_items = int(cfg.get("max_items") or cfg.get("max_videos") or 10)
        self.commentator = cfg.get("commentator") or source.id
        self.max_chars = int(cfg.get("max_chars") or 14000)

    def _expand_channel(self) -> list[str]:
        if not self.channel_url:
            return []
        if not _ytdlp_available():
            return []
        try:
            proc = subprocess.run(
                [
                    "yt-dlp",
                    "--flat-playlist",
                    "--dump-json",
                    "--playlist-end",
                    str(self.max_items),
                    self.channel_url,
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []
        urls: list[str] = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            vid = obj.get("id") or obj.get("url")
            if not vid:
                continue
            if str(vid).startswith("http"):
                urls.append(str(vid))
            else:
                urls.append(f"https://www.youtube.com/watch?v={vid}")
        return urls[: self.max_items]

    def _fetch_subs(self, url: str, work: Path) -> tuple[str, str | None]:
        outtmpl = str(work / "%(id)s")
        cmd = [
            "yt-dlp",
            "--skip-download",
            "--write-auto-sub",
            "--write-sub",
            "--sub-langs",
            ",".join(PREF_LANGS),
            "--sub-format",
            "vtt",
            "-o",
            outtmpl,
            url,
        ]
        proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=180)
        if proc.returncode != 0 and not list(work.glob("*.vtt")):
            raise RuntimeError(proc.stderr.strip()[:300] or "yt-dlp failed")
        # prefer zh-HK then yue then zh-Hant
        vtts = list(work.glob("*.vtt"))
        if not vtts:
            raise RuntimeError("no subtitles found")

        def rank(p: Path) -> int:
            name = p.name.lower()
            for i, lang in enumerate(PREF_LANGS):
                if lang.lower() in name:
                    return i
            return 99

        vtts.sort(key=rank)
        text = _vtt_to_text(vtts[0].read_text(encoding="utf-8", errors="ignore"))
        title = vtts[0].stem
        return text, title

    def run(self) -> tuple[CrawlRun, list[dict[str, Any]]]:
        started = datetime.now(HK_TZ)
        run_id = f"{started.strftime('%Y%m%d-%H%M%S')}-{self.source.id}"
        chunks: list[dict[str, Any]] = []
        errors: list[str] = []
        fetched = 0

        if not _ytdlp_available():
            finished = datetime.now(HK_TZ)
            run = CrawlRun(
                run_id=run_id,
                source_id=self.source.id,
                started_at=started,
                finished_at=finished,
                status=RunStatus.FAILED,
                error_message="yt-dlp not installed; pip install -e '.[style]'",
                duration_seconds=0.0,
                metadata={"purpose": "style"},
            )
            return run, []

        urls = list(self.urls)
        for u in self._expand_channel():
            if u not in urls:
                urls.append(u)
        urls = urls[: self.max_items]

        for url in urls:
            try:
                with tempfile.TemporaryDirectory(prefix="yt-style-") as tmp:
                    text, title = self._fetch_subs(url, Path(tmp))
                if len(text) < 40:
                    errors.append(f"{url}: subtitle text too short")
                    continue
                body = text[: self.max_chars]
                chunks.append(
                    {
                        "source_id": self.source.id,
                        "title": title or url,
                        "content": f"來源: {url}\n\n{body}",
                        "content_hash": _content_hash(body),
                        "metadata": {
                            "url": url,
                            "kind": "style_article",
                            "purpose": "style",
                            "commentator": self.commentator,
                            "domain_tags": ["style", "youtube", "commentary"],
                            "extractor": "yt-dlp-auto-sub",
                        },
                    }
                )
                fetched += 1
            except Exception as e:  # noqa: BLE001
                errors.append(f"{url}: {e}")

        finished = datetime.now(HK_TZ)
        if fetched == 0 and errors:
            status = RunStatus.FAILED
        elif errors:
            status = RunStatus.PARTIAL
        elif fetched == 0:
            status = RunStatus.SKIPPED
        else:
            status = RunStatus.SUCCESS

        run = CrawlRun(
            run_id=run_id,
            source_id=self.source.id,
            started_at=started,
            finished_at=finished,
            status=status,
            items_fetched=fetched,
            items_new=len(chunks),
            error_message="; ".join(errors[:5]) if errors else None,
            duration_seconds=round((finished - started).total_seconds(), 2),
            metadata={"purpose": "style", "url_count": len(urls)},
        )
        return run, chunks
