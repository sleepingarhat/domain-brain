"""Style-oriented article crawler for commentator sources.

Uses trafilatura when available, falls back to WebStaticConnector text extraction.
Respects robots.txt, polite delays, skips paywalls (401/402/403).
Marks chunks with kind=style_article for exemplar compilation.
"""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx

from ingestion.models import CrawlRun, RunStatus, Source

HK_TZ = timezone(timedelta(hours=8))
USER_AGENT = (
    "domain-brain-style/0.1 (+https://github.com/sleepingarhat/domain-brain; "
    "research-style-bot)"
)


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _extract_with_trafilatura(html: str, url: str) -> tuple[str, str | None]:
    try:
        import trafilatura
    except ImportError:
        return "", None
    text = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        favor_recall=True,
        url=url,
    ) or ""
    meta = trafilatura.extract_metadata(html)
    title = None
    if meta is not None:
        title = getattr(meta, "title", None)
    return text.strip(), title


def _extract_fallback(html: str) -> str:
    from connectors.web_static import _html_to_text

    return _html_to_text(html)


class StyleCrawlConnector:
    """Crawl listing / article URLs for style learning."""

    def __init__(self, source: Source, client: httpx.Client | None = None):
        self.source = source
        cfg = source.config or {}
        self.seed_urls: list[str] = list(
            cfg.get("seed_urls")
            or cfg.get("article_urls")
            or ([source.url] if source.url else [])
        )
        self.listing_urls: list[str] = list(cfg.get("listing_urls") or [])
        self.delay_seconds = float(cfg.get("delay_seconds") or 2.0)
        self.max_chars = int(cfg.get("max_chars") or 14000)
        self.max_items = int(cfg.get("max_items") or cfg.get("max_articles") or 20)
        self.commentator = cfg.get("commentator") or source.id
        self.respect_robots = bool(cfg.get("respect_robots", True))
        self.client = client or httpx.Client(
            timeout=30.0,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        self._robots: dict[str, RobotFileParser] = {}

    def _allowed(self, url: str) -> bool:
        if not self.respect_robots:
            return True
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self._robots:
            rp = RobotFileParser()
            robots_url = urljoin(origin, "/robots.txt")
            try:
                resp = self.client.get(robots_url)
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                else:
                    rp.parse([])
            except Exception:  # noqa: BLE001
                rp.parse([])
            self._robots[origin] = rp
        try:
            return bool(self._robots[origin].can_fetch(USER_AGENT, url))
        except Exception:  # noqa: BLE001
            return True

    def _discover_from_listings(self) -> list[str]:
        """Very light link harvest from listing pages (same-host http links)."""
        found: list[str] = []
        for listing in self.listing_urls:
            if not self._allowed(listing):
                continue
            try:
                resp = self.client.get(listing)
                if resp.status_code in (401, 402, 403):
                    continue
                resp.raise_for_status()
                host = urlparse(listing).netloc
                for href in self._hrefs(resp.text):
                    abs_url = urljoin(listing, href)
                    if urlparse(abs_url).netloc != host:
                        continue
                    if abs_url.rstrip("/") == listing.rstrip("/"):
                        continue
                    if abs_url not in found and abs_url not in self.seed_urls:
                        found.append(abs_url)
            except Exception:  # noqa: BLE001
                continue
            time.sleep(self.delay_seconds)
        return found

    @staticmethod
    def _hrefs(html: str) -> list[str]:
        import re

        return re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.I)

    def run(self) -> tuple[CrawlRun, list[dict[str, Any]]]:
        started = datetime.now(HK_TZ)
        run_id = f"{started.strftime('%Y%m%d-%H%M%S')}-{self.source.id}"
        chunks: list[dict[str, Any]] = []
        errors: list[str] = []
        fetched = 0

        urls = list(self.seed_urls)
        discovered = self._discover_from_listings()
        for u in discovered:
            if u not in urls:
                urls.append(u)
        urls = urls[: self.max_items]

        for i, url in enumerate(urls):
            if i:
                time.sleep(self.delay_seconds)
            if not self._allowed(url):
                errors.append(f"{url}: blocked by robots.txt")
                continue
            try:
                resp = self.client.get(url)
                if resp.status_code in (401, 402, 403):
                    errors.append(f"{url}: HTTP {resp.status_code} (paywall/blocked)")
                    continue
                resp.raise_for_status()
                text, title = _extract_with_trafilatura(resp.text, url)
                extractor = "trafilatura"
                if len(text) < 80:
                    text = _extract_fallback(resp.text)
                    title = title or self.source.name
                    extractor = "web_static_fallback"
                if len(text) < 80:
                    errors.append(f"{url}: too little text extracted")
                    continue
                body = text[: self.max_chars]
                if not title:
                    for line in body.splitlines():
                        if len(line.strip()) > 8:
                            title = line.strip()[:120]
                            break
                    title = title or self.source.name
                chunks.append(
                    {
                        "source_id": self.source.id,
                        "title": title,
                        "content": f"來源: {url}\n\n{body}",
                        "content_hash": _content_hash(body),
                        "metadata": {
                            "url": url,
                            "http_status": resp.status_code,
                            "kind": "style_article",
                            "purpose": "style",
                            "commentator": self.commentator,
                            "domain_tags": ["style", "commentary"],
                            "extractor": extractor,
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
            metadata={
                "seed_count": len(self.seed_urls),
                "listing_count": len(self.listing_urls),
                "purpose": "style",
            },
        )
        return run, chunks


def _trafilatura_available() -> bool:
    try:
        import trafilatura  # noqa: F401

        return True
    except ImportError:
        return False
