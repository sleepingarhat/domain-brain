"""Public GitHub repo docs connector (tianxi-repos).

Pulls a fixed allow-list of README / docs files plus recent human commit
subjects from PUBLIC GitHub repos, so the 天喜系統知識層 can be refreshed.

Safety:
- Read-only. Only raw.githubusercontent.com + api.github.com GET.
- Optional GITHUB_TOKEN / GH_TOKEN env is sent as a header only (never logged)
  to lift the anonymous rate limit; public repos work without it.
- Lines that look sensitive (tokens, secrets, admin paths, direct worker hosts,
  private keys …) are dropped before a chunk is written.
- Only emits docs whose content changed vs chunks already on disk.
- Chunk content is DATA, not instructions (see AGENTS.md).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

from ingestion.models import CrawlRun, RunStatus, Source

HK_TZ = timezone(timedelta(hours=8))
ROOT = Path(__file__).resolve().parents[1]
CHUNKS_DIR = ROOT / "ingestion" / "chunks"

SENSITIVE_RE = re.compile(
    r"(token|secret|passw|api[_-]?key|bearer|authorization|private key|"
    r"ADMIN_|_PAT\b|CF_API|CF_ACCOUNT|SUPABASE|STRIPE|WEBHOOK|\.env\b|"
    r"workers\.dev|/admin|/api/admin|cron-auth|ghp_[A-Za-z0-9]|sk_(live|test)_|"
    r"service[_-]?role|wrangler\.toml|account[_-]?id|"
    r"US\$|USD|Workers Paid|billing|扣款|預算|餘額|付款預警)",
    re.IGNORECASE,
)

BOT_RE = re.compile(r"(\[skip ci\]|^\[(data|manifest|sanity|audit)\]|^archive: official|^sync: 正式站發布|^speedpro: update|^chore\(weather\))")


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def redact(text: str) -> tuple[str, int]:
    """Drop whole lines that look sensitive. Returns (clean_text, dropped_lines)."""
    kept: list[str] = []
    dropped = 0
    for line in text.splitlines():
        if SENSITIVE_RE.search(line):
            dropped += 1
            continue
        kept.append(line)
    return "\n".join(kept).strip(), dropped


def split_text(text: str, size: int) -> list[str]:
    if len(text) <= size:
        return [text]
    parts: list[str] = []
    buf: list[str] = []
    n = 0
    for para in text.split("\n"):
        if n + len(para) + 1 > size and buf:
            parts.append("\n".join(buf))
            buf, n = [], 0
        buf.append(para[:size])
        n += len(para) + 1
    if buf:
        parts.append("\n".join(buf))
    return parts


def _existing_hashes(source_id: str) -> set[str]:
    out: set[str] = set()
    if not CHUNKS_DIR.exists():
        return out
    for path in CHUNKS_DIR.glob(f"*-{source_id}.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for ch in data if isinstance(data, list) else []:
            if isinstance(ch, dict) and ch.get("content_hash"):
                out.add(str(ch["content_hash"]))
    return out


class GithubDocsConnector:
    def __init__(self, source: Source, client: httpx.Client | None = None):
        self.source = source
        cfg = source.config or {}
        self.repos: list[dict[str, Any]] = list(cfg.get("repos") or [])
        self.max_chars = int(cfg.get("max_chars") or 6000)
        self.commit_limit = int(cfg.get("commit_limit") or 30)
        headers = {"User-Agent": "domain-brain/0.2 (tianxi-repos docs refresh)"}
        tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        self._api_headers = dict(headers)
        if tok:
            self._api_headers["Authorization"] = f"Bearer {tok}"
        self.client = client or httpx.Client(timeout=30.0, follow_redirects=True, headers=headers)

    def _head_sha(self, repo: str, branch: str) -> str | None:
        r = self.client.get(f"https://api.github.com/repos/{repo}/commits/{branch}", headers=self._api_headers)
        if r.status_code != 200:
            return None
        return str(r.json().get("sha") or "")[:8] or None

    def _doc_chunks(self, repo: str, branch: str, sha: str | None, path: str, now: str) -> tuple[list[dict], int]:
        url = f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
        r = self.client.get(url)
        if r.status_code != 200:
            raise RuntimeError(f"{repo}/{path} HTTP {r.status_code}")
        clean, dropped = redact(r.text)
        chunks: list[dict] = []
        parts = split_text(clean, self.max_chars)
        for i, part in enumerate(parts, 1):
            if not part.strip():
                continue
            title = f"{repo}:{path}" + (f" ({i}/{len(parts)})" if len(parts) > 1 else "")
            chunks.append(
                {
                    "source_id": self.source.id,
                    "title": title,
                    "content": part,
                    "content_hash": _hash(f"{repo}|{path}|{part}"),
                    "metadata": {
                        "kind": "repo_doc",
                        "repo": repo,
                        "path": path,
                        "commit": sha,
                        "url": f"https://github.com/{repo}/blob/{branch}/{path}",
                        "fetched_at": now,
                        "redacted_lines": dropped,
                        "domain_tags": ["tianxi", "system"],
                    },
                }
            )
        return chunks, dropped

    def _commit_chunk(self, repo: str, branch: str, now: str) -> dict | None:
        r = self.client.get(
            f"https://api.github.com/repos/{repo}/commits",
            params={"sha": branch, "per_page": 100},
            headers=self._api_headers,
        )
        if r.status_code != 200:
            raise RuntimeError(f"{repo} commits HTTP {r.status_code}")
        lines: list[str] = []
        for c in r.json():
            msg = ((c.get("commit") or {}).get("message") or "").splitlines()[0].strip()
            date = (((c.get("commit") or {}).get("author") or {}).get("date") or "")[:10]
            if not msg or BOT_RE.search(msg) or SENSITIVE_RE.search(msg):
                continue
            lines.append(f"{date} {str(c.get('sha'))[:8]} {msg[:160]}")
            if len(lines) >= self.commit_limit:
                break
        if not lines:
            return None
        body = "\n".join(lines)
        return {
            "source_id": self.source.id,
            "title": f"{repo}:recent-commits",
            "content": body,
            "content_hash": _hash(f"{repo}|commits|{body}"),
            "metadata": {
                "kind": "repo_doc",
                "repo": repo,
                "path": "(git log)",
                "url": f"https://github.com/{repo}/commits/{branch}",
                "fetched_at": now,
                "domain_tags": ["tianxi", "dev-history"],
            },
        }

    def run(self) -> tuple[CrawlRun, list[dict]]:
        started = datetime.now(HK_TZ)
        now = started.isoformat(timespec="seconds")
        seen = _existing_hashes(self.source.id)
        out: list[dict] = []
        errors: list[str] = []
        fetched = 0
        dropped_total = 0
        for spec in self.repos:
            repo = str(spec.get("repo") or "")
            branch = str(spec.get("branch") or "main")
            if not repo:
                continue
            try:
                sha = self._head_sha(repo, branch)
            except httpx.HTTPError as e:  # noqa: PERF203
                sha = None
                errors.append(f"{repo} head: {type(e).__name__}")
            for path in spec.get("paths") or []:
                try:
                    chunks, dropped = self._doc_chunks(repo, branch, sha, str(path), now)
                except (httpx.HTTPError, RuntimeError) as e:
                    errors.append(str(e) if isinstance(e, RuntimeError) else f"{repo}/{path}: {type(e).__name__}")
                    continue
                fetched += len(chunks)
                dropped_total += dropped
                out.extend(c for c in chunks if c["content_hash"] not in seen)
            if spec.get("commits", True):
                try:
                    cc = self._commit_chunk(repo, branch, now)
                except (httpx.HTTPError, RuntimeError) as e:
                    cc = None
                    errors.append(str(e) if isinstance(e, RuntimeError) else f"{repo} commits: {type(e).__name__}")
                if cc:
                    fetched += 1
                    if cc["content_hash"] not in seen:
                        out.append(cc)
        finished = datetime.now(HK_TZ)
        if errors and not fetched:
            status = RunStatus.FAILED
        elif errors:
            status = RunStatus.PARTIAL
        elif not out:
            status = RunStatus.SKIPPED
        else:
            status = RunStatus.SUCCESS
        run = CrawlRun(
            run_id=f"{started.strftime('%Y%m%d-%H%M%S')}-{self.source.id}",
            source_id=self.source.id,
            started_at=started,
            finished_at=finished,
            status=status,
            items_fetched=fetched,
            items_new=len(out),
            items_skipped=fetched - len(out),
            error_message="; ".join(errors)[:500] or None,
            duration_seconds=round((finished - started).total_seconds(), 2),
            metadata={"redacted_lines": dropped_total},
        )
        return run, out
