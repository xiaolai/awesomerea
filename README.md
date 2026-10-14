# awesomerea

A curated list of projects that use [REA (Reverse Engineer Anything)](https://github.com/morluto/rea) with AI coding agents.

> **Status: early.** This repository currently holds the collector and its first snapshots. The curated list is not published yet. Snapshot entries are candidates for review, not endorsements.

## What is REA

REA is an MIT-licensed MCP server and CLI that lets a coding agent inspect software, from application behavior down to native binaries, and return the evidence behind each finding. The upstream project is [morluto/rea](https://github.com/morluto/rea).

## Inclusion rules

An entry must:

- use REA in a way a reader can reproduce, or be a substantive original writeup;
- state the REA version it was run against;
- state its limitations;
- not copy another project's protected code or assets, in line with the upstream [DISCLAIMER](https://github.com/morluto/rea/blob/main/DISCLAIMER.md);
- not ask readers to run unverified installers.

Mirrors, verbatim or lightly edited copies of the upstream README, and download pages that are not the upstream release are excluded.

## How candidates are collected

`tools/collect.py` searches GitHub through the `gh` CLI and writes a dated snapshot under `data/snapshots/`. It is read-only and does not publish anything.

```sh
python3 tools/collect.py --limit 100
```

Each candidate gets one of these statuses:

| Status | Meaning |
| --- | --- |
| `needs-human-review` | Names the upstream project or its npm package, and its README is original. |
| `weak-match` | Only a generic phrase matched. Usually not a REA user. |
| `upstream-copy` | README is at least 40% identical (by non-blank lines) to upstream's. |

Flags such as `pipe-to-shell`, `download-lure` and `presents-rea-as-target` are hints for a human, not verdicts.

The collector cannot judge whether a project is good. Every entry is checked by hand before it reaches the list.

## Layout

- `tools/collect.py`: the collector (standard library only, plus `gh`).
- `data/snapshots/<date>/`: each run's candidates, rejected repos, errors and summary.
- `data/cache/`: README cache, git-ignored.
