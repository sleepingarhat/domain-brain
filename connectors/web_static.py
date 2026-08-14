"""Polite static-page fetcher for commentary / news seed URLs.

Respect rate limits. Does NOT bypass paywalls or logins.
Only fetches publicly reachable HTML and extracts rough text.
"""

from __future__ import annotations

import hashlib
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from html.parser import HTMLParser

import httpx

from ingestion.models import CrawlRun, RunStatus, Source

HK_TZ = timezone(timedelta(hours=8))


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "noscript", "svg", "nav", "footer", "header"}:
            self._skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg", "nav", "footer", "header"}:
            self._skip = max(0, self._skip - 1)

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        t = data.strip()
        if t:
            self._chunks.append(t)

    def text(self) -> str:
        raw = "\n".join(self._chunks)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


def _html_to_text(html: str) -> str:
    p = _TextExtractor()
    try:
        p.feed(html)
        p.close()
    except Exception:  # noqa: BLE001
        return re.sub(r"<[^>]+>", " ", html)
    return p.text()


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


class WebStaticConnector:
    def __init__(self, source: Source, client: httpx.Client | None = None):
        self.source = source
        self.seed_urls: list[str] = list(
            source.config.get("seed_urls") or ([source.url] if source.url else [])
        )
        self.delay_seconds = float(source.config.get("delay_seconds") or 1.5)
        self.max_chars = int(source.config.get("max_chars") or 12000)
        self.client = client or httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "domain-brain/0.2 (+https://github.com/sleepingarhat/domain-brain; "
                    "research-knowledge-bot)"
                )
            },
        )

    def run(self) -> tuple[CrawlRun, list[dict[str, Any]]]:
        started = datetime.now(HK_TZ)
        run_id = f"{started.strftime('%Y%m%d-%H%M%S')}-{self.source.id}"
        chunks: list[dict[str, Any]] = []
        errors: list[str] = []
        fetched = 0

        for i, url in enumerate(self.seed_urls):
            if i:
                time.sleep(self.delay_seconds)
            try:
                resp = self.client.get(url)
                if resp.status_code in (401, 403, 402):
                    errors.append(f"{url}: HTTP {resp.status_code} (paywall/blocked)")
                    continue
                resp.raise_for_status()
                text = _html_to_text(resp.text)
                if len(text) < 80:
                    errors.append(f"{url}: too little text extracted")
                    continue
                body = text[: self.max_chars]
                title = self.source.name
                # crude title from first non-empty line
                for line in body.splitlines():
                    if len(line.strip()) > 8:
                        title = line.strip()[:120]
                        break
                chunks.append(
                    {
                        "source_id": self.source.id,
                        "title": title,
                        "content": f"來源: {url}\n\n{body}",
                        "content_hash": _content_hash(body),
                        "metadata": {"url": url, "http_status": resp.status_code},
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
            items_updated=0,
            items_skipped=0,
            error_message="; ".join(errors[:5]) if errors else None,
            duration_seconds=round((finished - started).total_seconds(), 2),
            content_hash=None,
            metadata={"seed_count": len(self.seed_urls)},
        )
        return run, chunks
