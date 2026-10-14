#!/usr/bin/env python3
"""Build the tabbed static site in docs/ from README.md and content/*.md.

Each tab is one Markdown source. pandoc converts it to an HTML fragment, and this
script wraps every fragment in the same page shell with a shared tab bar.

Requires pandoc on PATH. Commit the regenerated docs/ together with the source.
Usage:  python3 tools/build_site.py
"""

from __future__ import annotations

import html
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SANITIZER = ROOT / "tools" / "sanitize.lua"

# Defence in depth: the filter should already remove these. If one survives, fail the build.
ACTIVE_CONTENT = re.compile(r"(?i)<script|javascript:|vbscript:|\bon\w+\s*=\s*[\"']")
URL_ATTRIBUTE = re.compile(r'\b(?:href|src)\s*=\s*"([^"]*)"', re.IGNORECASE)
ALLOWED_SCHEMES = {"http", "https", "mailto"}


def first_unsafe_url(fragment: str) -> str | None:
    """Return the first href or src whose scheme could run script, or None.

    This reads the HTML the browser will read, so it is independent of the pandoc filter
    and catches what a filter's parse of the Markdown might miss.
    """
    for match in URL_ATTRIBUTE.finditer(fragment):
        value = html.unescape(match.group(1))
        normalised = re.sub(r"[\x00-\x20\x7f]", "", value).lower()
        scheme = re.match(r"([a-z][a-z0-9+.-]*):", normalised)
        if scheme and scheme.group(1) not in ALLOWED_SCHEMES:
            return value
    return None

# (tab label, Markdown source, output file). The first entry is the home page.
TABS = [
    ("README", ROOT / "README.md", "index.html"),
    ("List", ROOT / "content" / "list.md", "list.html"),
    ("Pending", ROOT / "content" / "pending.md", "pending.html"),
    ("Submit", ROOT / "content" / "submit.md", "submit.html"),
    ("Rules", ROOT / "content" / "rules.md", "rules.html"),
]

STYLE = """
:root { color-scheme: light dark; --fg:#1f2328; --muted:#59636e; --bg:#ffffff;
  --border:#d1d9e0; --accent:#0969da; --code:#f6f8fa; }
@media (prefers-color-scheme: dark) {
  :root { --fg:#e6edf3; --muted:#9198a1; --bg:#0d1117; --border:#3d444d;
    --accent:#4493f8; --code:#151b23; } }
* { box-sizing: border-box; }
body { margin:0; font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  color:var(--fg); background:var(--bg); }
header { border-bottom:1px solid var(--border); padding:0 24px; }
header h1 { font-size:20px; margin:0; padding:16px 0 8px; }
nav.tabs { display:flex; gap:4px; flex-wrap:wrap; }
nav.tabs a { padding:8px 14px; color:var(--muted); text-decoration:none;
  border-bottom:2px solid transparent; }
nav.tabs a:hover { color:var(--fg); }
nav.tabs a[aria-current="page"] { color:var(--fg); border-bottom-color:var(--accent); font-weight:600; }
main { max-width:860px; margin:0 auto; padding:24px; }
h1,h2,h3 { line-height:1.25; }
h2 { border-bottom:1px solid var(--border); padding-bottom:6px; margin-top:32px; }
a { color:var(--accent); }
code { background:var(--code); padding:2px 5px; border-radius:6px; font-size:85%; }
pre { background:var(--code); padding:16px; border-radius:6px; overflow:auto; }
pre code { padding:0; background:none; }
table { border-collapse:collapse; width:100%; display:block; overflow-x:auto; }
th,td { border:1px solid var(--border); padding:6px 10px; text-align:left; vertical-align:top; }
th { background:var(--code); }
blockquote { margin:0; padding:0 1em; color:var(--muted); border-left:4px solid var(--border); }
footer { max-width:860px; margin:0 auto; padding:0 24px 32px; color:var(--muted); font-size:14px; }
"""


def render_fragment(source: pathlib.Path) -> str:
    """Convert one Markdown file to an HTML fragment. Fails loudly if pandoc does."""
    proc = subprocess.run(
        ["pandoc", "--from", "gfm", "--to", "html5", "--lua-filter", str(SANITIZER), str(source)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(f"pandoc failed for {source}: {proc.stderr.strip()}")
    if ACTIVE_CONTENT.search(proc.stdout):
        raise SystemExit(f"active content survived sanitising in {source}; refusing to build")
    unsafe = first_unsafe_url(proc.stdout)
    if unsafe is not None:
        raise SystemExit(f"unsafe URL survived sanitising in {source}: {unsafe!r}; refusing to build")
    return proc.stdout


def tab_bar(active_file: str) -> str:
    links = []
    for label, _, out in TABS:
        current = ' aria-current="page"' if out == active_file else ""
        links.append(f'<a href="{out}"{current}>{html.escape(label)}</a>')
    return '<nav class="tabs" aria-label="Sections">' + "".join(links) + "</nav>"


def page(label: str, body: str, out_file: str) -> str:
    title = "awesomerea" if out_file == "index.html" else f"{label} · awesomerea"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{STYLE}</style>
</head>
<body>
<header>
<h1><a href="index.html" style="color:inherit;text-decoration:none">awesomerea</a></h1>
{tab_bar(out_file)}
</header>
<main>
{body}
</main>
<footer>Generated by tools/build_site.py from README.md and content/. Edit the Markdown, not this file.</footer>
</body>
</html>
"""


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    for label, source, out_file in TABS:
        if not source.exists():
            raise SystemExit(f"missing source for tab {label}: {source}")
        fragment = render_fragment(source)
        (DOCS / out_file).write_text(page(label, fragment, out_file), encoding="utf-8")
        print(f"wrote docs/{out_file} from {source.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
