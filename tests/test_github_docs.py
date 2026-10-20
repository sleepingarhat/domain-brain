from brain.extract import extract_mentions
from connectors.github_docs import redact, split_text


def test_redact_drops_sensitive_lines():
    text = "公開說明\nneeds secret CF_API_TOKEN here\nhttps://x.workers.dev/api\n/admin/engine-health\n凍結 T−90"
    clean, dropped = redact(text)
    assert dropped == 3
    assert "公開說明" in clean and "凍結 T−90" in clean
    assert "workers.dev" not in clean and "TOKEN" not in clean and "/admin" not in clean


def test_split_text_respects_size():
    parts = split_text("\n".join(["行" * 50] * 10), 120)
    assert len(parts) > 1
    assert all(len(p) <= 120 for p in parts)


def test_repo_doc_chunk_only_links_source_page():
    chunk = {
        "source_id": "tianxi-repos",
        "title": "sleepingarhat/tianxi-racing:MODEL.md",
        "content": "第1名 3號 某馬 騎師: 某騎師\n場地：沙田\nTX-Oracle",
        "content_hash": "abc",
        "metadata": {"kind": "repo_doc", "repo": "sleepingarhat/tianxi-racing", "path": "MODEL.md", "commit": "f467acb7", "fetched_at": "2026-10-20T13:00:00+08:00"},
    }
    ms = extract_mentions(chunk)
    assert len(ms) == 1
    assert ms[0].kind == "source" and ms[0].name == "tianxi-repos"
    assert "MODEL.md" in ms[0].snippet
