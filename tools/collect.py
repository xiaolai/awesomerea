#!/usr/bin/env python3
"""Collect GitHub projects that use REA (morluto/rea) and write a dated snapshot.

Read-only: searches GitHub through the `gh` CLI and writes local files only.
Nothing is published, committed or pushed by this script.

Output, per run:
  data/snapshots/<UTC date>/candidates.json   every repo that passed the relevance rule
  data/snapshots/<UTC date>/rejected.json     repos that were dropped, with the reason
  data/snapshots/<UTC date>/errors.json       any failed query or README fetch (never silent)
  data/snapshots/<UTC date>/summary.md        human-readable table

Usage:  python3 tools/collect.py [--limit N]
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
UPSTREAM = "morluto/rea"

# Search queries. Repo search matches names and descriptions; code search matches file text.
REPO_QUERIES = ["rea-agents", '"Reverse Engineer Anything"', "morluto/rea", "reverse-engineer-anything"]
CODE_QUERIES = ["rea-agents", "morluto/rea", "reverse-engineer-anything"]

# Relevance rule: the README must name the upstream project, not just share a word with it.
RELEVANCE_PATTERNS = [
    re.compile(r"morluto/rea\b", re.I),
    re.compile(r"\brea-agents\b", re.I),
    re.compile(r"reverse engineer anything", re.I),
]

# Hints for human review. These never exclude a repo; they only flag it.
SUSPICION_PATTERNS = {
    "pipe-to-shell": re.compile(r"curl[^\n|]*\|\s*(sh|bash)\b"),
    # Phrases that sell a zip or a "free download" as REA. Upstream's own text ("verifies the
    # official download") must not match, so "official download" is deliberately absent.
    "download-lure": re.compile(r"(?i)free\s+download|download\s+the\s+[^\n]{0,20}zip|local\s+(mcp\s+)?zip"),
    "bare-download-link": re.compile(r"(?i)download\s*[:：]\s*\S*[🡇⬇]"),
}

# Repos confirmed as lures or impersonators, with the evidence. Checked before any README
# fetch, so an excluded repo never reaches the candidate list.
EXCLUSIONS_FILE = ROOT / "data" / "exclusions.json"

# Only a version written next to the REA name or the npm package counts.
# A bare "22.19.0" (a Node.js version, for example) must not be read as an REA version.
REA_VERSION = re.compile(r"(?:rea-agents@|\bREA\s+v?)(\d+\.\d+\.\d+)")

# Flag, not exclude: text that presents REA as a target to defeat.
ADVERSARIAL = re.compile(r"(?i)(defeat|evade|bypass|counter)\w*[^\n]{0,80}(morluto/rea|\bREA\b)")

# A README whose lines are at least this similar to upstream's is treated as a copy.
# Observed scores are bimodal: copies (edited or verbatim) sit at 0.65-1.0, original
# READMEs at 0.0-0.1. Any cut between those bands separates them; 0.4 sits in the gap.
COPY_THRESHOLD = 0.4
CACHE_DAYS = 7


class CollectError(RuntimeError):
    pass


def line_set(text: str) -> set[str]:
    return {ln.strip() for ln in text.splitlines() if ln.strip()}


def first_heading(text: str) -> str:
    """Title of the README: its first Markdown heading, normalised for comparison."""
    for line in text.splitlines():
        if line.startswith("#"):
            return line.lstrip("#").strip().lower()
    return ""


def similarity(a: str, b: str) -> float:
    """Jaccard similarity of non-blank lines. Cheap, and robust to whitespace changes."""
    sa, sb = line_set(a), line_set(b)
    return len(sa & sb) / len(sa | sb) if sa and sb else 0.0


def gh_json(args: list[str]) -> object:
    """Run `gh` with an argument list (no shell) and return parsed JSON. Fails loudly."""
    proc = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise CollectError(f"gh {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}")
    try:
        return json.loads(proc.stdout or "null")
    except json.JSONDecodeError as exc:
        raise CollectError(f"gh {' '.join(args)} returned non-JSON output: {exc}") from exc


def search_repos(query: str, limit: int) -> list[dict]:
    fields = "fullName,description,stargazersCount,isFork,isArchived,pushedAt,url"
    return gh_json(["search", "repos", query, "--limit", str(limit), "--json", fields]) or []


def search_code(query: str, limit: int) -> list[str]:
    hits = gh_json(["search", "code", query, "--limit", str(limit), "--json", "repository,path"]) or []
    return [h["repository"]["nameWithOwner"] for h in hits]


CACHE_DIR = ROOT / "data" / "cache" / "readme"


def fetch_readme(full_name: str) -> str:
    """Return the README text, using a local cache younger than CACHE_DAYS."""
    cached = CACHE_DIR / (full_name.replace("/", "__") + ".md")
    if cached.exists():
        age = dt.datetime.now(dt.timezone.utc).timestamp() - cached.stat().st_mtime
        if age < CACHE_DAYS * 86400:
            return cached.read_text(encoding="utf-8")
    data = gh_json(["api", f"repos/{full_name}/readme"])
    if not isinstance(data, dict) or "content" not in data:
        raise CollectError(f"README response for {full_name} has no content field")
    text = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cached.write_text(text, encoding="utf-8")
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--limit", type=int, default=100, help="results per search query (max 100)")
    args = parser.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    out_dir = ROOT / "data" / "snapshots" / now.strftime("%Y-%m-%d")
    out_dir.mkdir(parents=True, exist_ok=True)

    errors: list[dict] = []
    seen: dict[str, dict] = {}  # fullName -> repo info, with the queries that found it
    code_hits: set[str] = set()

    for q in REPO_QUERIES:
        try:
            for repo in search_repos(q, args.limit):
                entry = seen.setdefault(repo["fullName"], {**repo, "found_by": []})
                entry["found_by"].append(f"repo:{q}")
        except CollectError as exc:
            errors.append({"stage": "repo-search", "query": q, "error": str(exc)})
        time.sleep(2)  # stay under the search rate limit

    for q in CODE_QUERIES:
        try:
            code_hits.update(search_code(q, args.limit))
        except CollectError as exc:
            errors.append({"stage": "code-search", "query": q, "error": str(exc)})
        time.sleep(3)

    # Code hits that the repo search did not return still need the same README check.
    for name in sorted(code_hits):
        if name not in seen:
            seen[name] = {"fullName": name, "found_by": ["code"]}
        else:
            seen[name]["found_by"].append("code")

    upstream_readme = fetch_readme(UPSTREAM)
    excluded = {e["fullName"].lower(): e for e in json.loads(EXCLUSIONS_FILE.read_text())}

    candidates: list[dict] = []
    rejected: list[dict] = []

    for name in sorted(seen):
        repo = seen[name]
        if name.lower() == UPSTREAM:
            rejected.append({"fullName": name, "reason": "upstream project itself"})
            continue
        if name.lower() in excluded:
            rejected.append({"fullName": name, "reason": "excluded: " + excluded[name.lower()]["reason"]})
            continue
        try:
            readme = fetch_readme(name)
        except CollectError as exc:
            errors.append({"stage": "readme", "repo": name, "error": str(exc)})
            continue

        # Strong match names the upstream project or its npm package. A generic phrase is weak.
        strong = [p.pattern for p in RELEVANCE_PATTERNS[:2] if p.search(readme)]
        weak = [p.pattern for p in RELEVANCE_PATTERNS[2:] if p.search(readme)]
        if not strong and not weak:
            rejected.append({"fullName": name, "reason": "README does not name REA", "found_by": repo["found_by"]})
            continue

        copy_score = similarity(readme, upstream_readme)
        flags = [label for label, pat in SUSPICION_PATTERNS.items() if pat.search(readme)]
        if ADVERSARIAL.search(readme):
            flags.append("presents-rea-as-target")

        # Mirrors reuse upstream's title as well as its text, so compare the first heading too.
        if copy_score >= COPY_THRESHOLD or first_heading(readme) == first_heading(upstream_readme):
            rejected.append({"fullName": name, "reason": "upstream copy or mirror", "upstream_similarity": round(copy_score, 3)})
            continue
        if not strong:
            rejected.append({"fullName": name, "reason": "generic phrase only; not a REA user", "found_by": repo["found_by"]})
            continue

        candidates.append(
            {
                "fullName": name,
                "url": repo.get("url", f"https://github.com/{name}"),
                "description": repo.get("description") or "",
                "stars": repo.get("stargazersCount"),
                "isFork": repo.get("isFork"),
                "isArchived": repo.get("isArchived"),
                "pushedAt": repo.get("pushedAt"),
                "found_by": repo["found_by"],
                "relevance_matches": strong + weak,
                "upstream_similarity": round(copy_score, 3),
                "rea_versions_mentioned": sorted({m.group(1) for m in REA_VERSION.finditer(readme)}),
                "suspicion_flags": flags,
                "status": "needs-human-review",
            }
        )

    candidates.sort(key=lambda c: (-(c["stars"] or 0), c["fullName"].lower()))

    (out_dir / "candidates.json").write_text(json.dumps(candidates, indent=2, ensure_ascii=False) + "\n")
    (out_dir / "rejected.json").write_text(json.dumps(rejected, indent=2, ensure_ascii=False) + "\n")
    (out_dir / "errors.json").write_text(json.dumps(errors, indent=2, ensure_ascii=False) + "\n")

    by_status: dict[str, list[dict]] = {}
    for c in candidates:
        by_status.setdefault(c["status"], []).append(c)

    lines = [
        f"# Snapshot {now.strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"Rejected: {len(rejected)} · Errors: {len(errors)}",
        "",
    ]
    for status in ("needs-human-review", "weak-match", "upstream-copy"):
        group = by_status.get(status, [])
        lines += [
            f"## {status} ({len(group)})",
            "",
            "| Repo | Stars | Archived | Similarity | REA versions | Flags |",
            "| --- | ---: | --- | ---: | --- | --- |",
        ]
        for c in group:
            lines.append(
                f"| [{c['fullName']}]({c['url']}) | {c['stars']} | {c['isArchived']} "
                f"| {c['upstream_similarity']} | {', '.join(c['rea_versions_mentioned']) or '-'} "
                f"| {', '.join(c['suspicion_flags']) or '-'} |"
            )
        lines.append("")
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n")

    print(f"snapshot: {out_dir}")
    print(" ".join(f"{s}={len(by_status.get(s, []))}" for s in ("needs-human-review", "weak-match", "upstream-copy")))
    print(f"rejected={len(rejected)} errors={len(errors)}")
    if errors:
        print("ERRORS present; see errors.json. The snapshot is incomplete.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
