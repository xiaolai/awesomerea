## Inclusion rules

An entry must:

- use REA in a way a reader can reproduce, or be a substantive original writeup;
- state the REA version it was run against;
- state its limitations;
- not copy another project's protected code or assets, in line with the upstream [DISCLAIMER](https://github.com/morluto/rea/blob/main/DISCLAIMER.md);
- not ask readers to run unverified installers.

Mirrors, verbatim or lightly edited copies of the upstream README, download pages that are not the upstream release, and projects whose stated purpose is to defeat REA are excluded.

## How candidates are collected

`tools/collect.py` searches GitHub through the `gh` CLI and writes a dated snapshot under `data/snapshots/`. It is read-only and does not publish anything. Repositories excluded for a reason are listed in `data/exclusions.json`.

```sh
python3 tools/collect.py --limit 100
```

Each snapshot candidate is marked `needs-human-review`. Upstream copies, mirrors and repositories that match only a generic phrase are recorded in `rejected.json` with a reason.

Flags such as `pipe-to-shell`, `download-lure` and `presents-rea-as-target` are hints for a human, not verdicts. The collector cannot judge whether a project is good; every entry is checked by hand before it reaches the list.

## Layout

- `tools/collect.py`: the collector (standard library only, plus `gh`).
- `data/exclusions.json`: repositories excluded, with reasons.
- `data/snapshots/<date>/`: each run's candidates, rejected repos, errors and summary.
- `data/cache/`: README cache, git-ignored.

## Publishing the site

The tabs are generated, not hand-written.

1. Edit `README.md` or a file in `content/`.
2. Run `python3 tools/build_site.py`. It needs `pandoc` on the PATH and rewrites `docs/*.html`.
3. Commit the source and the regenerated `docs/` together.

GitHub Pages serves the `docs/` folder on `main`. Enable it under Settings > Pages, with source "Deploy from a branch", branch `main`, folder `/docs`.
