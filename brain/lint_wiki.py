"""Read-only wiki lint. Does not write pages."""

from __future__ import annotations

from brain.wiki import SECTIONS, WIKI_DIR, iter_pages


def lint_wiki() -> dict:
    pages = iter_pages()
    issues: list[str] = []
    by_id: dict[str, str] = {}
    titles: dict[tuple[str, str], str] = {}

    if not pages:
        issues.append("wiki 未有頁（先跑 python -m brain.cli compile）")
        return {"ok": False, "pages": 0, "issues": issues}

    for page in pages:
        rel = str(page.path.relative_to(WIKI_DIR.parent))
        ptype = page.meta.get("type")
        pid = page.meta.get("id")
        if not ptype:
            issues.append(f"{rel}: 缺 type")
        if not pid:
            issues.append(f"{rel}: 缺 id")
        elif pid in by_id:
            issues.append(f"{rel}: 重複 id {pid}（亦見 {by_id[pid]}）")
        else:
            by_id[str(pid)] = rel
        key = (str(ptype), page.title)
        if key in titles and ptype not in ("index", "log", "style"):
            issues.append(f"{rel}: 同類型重複 title {page.title}")
        else:
            titles[key] = rel
        for sec in SECTIONS:
            if sec not in page.sections:
                issues.append(f"{rel}: 缺章節 {sec}")
        obs = (page.sections.get("觀察") or "").strip()
        if ptype in ("horse", "jockey", "trainer", "course") and not obs:
            issues.append(f"{rel}: 實體頁無觀察（未連結）")

    return {
        "ok": len(issues) == 0,
        "pages": len(pages),
        "issues": issues[:80],
        "issue_count": len(issues),
    }
