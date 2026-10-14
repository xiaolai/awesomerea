# awesomerea

A curated list of projects that use [REA (Reverse Engineer Anything)](https://github.com/morluto/rea) with AI coding agents.

> **Status: first version.** Entries were checked by hand. Each one names the REA version its README states, or is marked pending. The version field comes from the entry's own README, not from our testing.

## What is REA

REA is an MIT-licensed MCP server and CLI that lets a coding agent inspect software, from application behavior down to native binaries, and return the evidence behind each finding. The upstream project is [morluto/rea](https://github.com/morluto/rea), and its official site is [rea.tools](https://rea.tools/).

## Cases and writeups

- [NullLabTests/OpenBSD_netcat_REA](https://github.com/NullLabTests/OpenBSD_netcat_REA): static analysis of Ubuntu's `netcat-openbsd` with REA and Ghidra. Each claim links to an artifact; the README lists its limits. REA 6.2.0.
- [az9713/REA-demo](https://github.com/az9713/REA-demo): REA analyzing its own installed package, with the run recorded as a receipt. REA 6.3.0.
- [ringozzt/rea-research](https://github.com/ringozzt/rea-research): a Chinese technical study of REA. The README cites REA 5.0.0 and 6.0.0; upstream is now newer, so check the current release.
- [inematds/rea-engenharia-reversa](https://github.com/inematds/rea-engenharia-reversa): a Portuguese guide to REA. REA 6.3.0.
- [valorisa/Reverse-Engineer-Anything](https://github.com/valorisa/Reverse-Engineer-Anything): an unofficial French guide. It cites REA 3.1.0, which is out of date; check the current release before following it.

## Tools and integrations

- [czcdr/dsh-plugin-rea](https://github.com/czcdr/dsh-plugin-rea): brings REA into DeepSeek Harness as `mcp__rea__*` tools. REA 6.4.0.
- [Fanqi89/dsh-rea](https://github.com/Fanqi89/dsh-rea): a configuration-only DeepSeek Harness bundle for REA. REA 6.4.0.
- [sheilacraig/dsh-rea-mcp](https://github.com/sheilacraig/dsh-rea-mcp): a single-file DeepSeek Harness bridge to REA's stdio server. REA 6.4.0.
- [zhaofeng130/dsh-rea](https://github.com/zhaofeng130/dsh-rea): REA's skill and two tools inside DeepSeek Harness. REA 6.3.0.
- [ya123-4/rea-dsh-plugin](https://github.com/ya123-4/rea-dsh-plugin): a DeepSeek Harness plugin that ships the REA server and skill together. REA 6.3.0.
- [alexmi256/rea-agent-docker](https://github.com/alexmi256/rea-agent-docker): a Docker image and Compose stack that runs REA with its analysis engines. REA 6.4.0.
- [dazeb/rea-codex-plugin](https://github.com/dazeb/rea-codex-plugin): a Codex plugin marketplace for REA. REA 6.3.0.
- [cognixws/picode-rea](https://github.com/cognixws/picode-rea): a PiCode extension for REA. REA 6.1.0.
- [ghirardo-giorgio/REA-MCP-Split](https://github.com/ghirardo-giorgio/REA-MCP-Split): splits REA's 139 MCP tools into domain-specific servers to reduce per-session token cost. REA 6.3.0.
- [UnknownHacker1/rea-groundtruth](https://github.com/UnknownHacker1/rea-groundtruth): checks what REA reports against code whose behavior is known. Tested with REA 6.4.0.
- [bioassembly/antigravity-sage](https://github.com/bioassembly/antigravity-sage): a configuration harness for Google Antigravity CLI that registers REA. REA 6.4.0.
- [dav1dngy/era-agent](https://github.com/dav1dngy/era-agent): ERA, a reverse-engineering agent built on REA. REA 6.4.0.

## Resources

- [ZooHero500/reatool](https://github.com/ZooHero500/reatool): unofficial REA tutorials and FAQ. Checked against rea-agents 6.4.0 on 2026-10-12.
- [sqwu/rea-gems](https://github.com/sqwu/rea-gems): an auto-updated gallery of REA cases.
- [miles990/rea-case-rankings](https://github.com/miles990/rea-case-rankings): a daily ranking of REA cases.
- [ylwl1997/rea-run](https://github.com/ylwl1997/rea-run): unofficial bilingual community docs for REA. The site states it is independent of the REA maintainers.
- [dmcchesney96/Reverse-engineer-anything](https://github.com/dmcchesney96/Reverse-engineer-anything): a collection of AI-assisted reverse-engineering work, with REA as its included project.

## Pending verification

These entries are relevant but do not yet meet the inclusion rules. Each one lacks a stated REA version, or its install path needs checking.

- [ylwl1997/rea-run-lab](https://github.com/ylwl1997/rea-run-lab): a teaching lab against a bundled demo. No REA version stated.
- [Nowng/rea-mcp](https://github.com/Nowng/rea-mcp): a LM Studio plugin for REA. No REA version stated.
- [caixuf/dsh-rea](https://github.com/caixuf/dsh-rea): a DeepSeek Harness plugin for REA. No REA version stated.
- [thewild001/mcp-rea](https://github.com/thewild001/mcp-rea): a FastMCP wrapper that launches REA's official MCP server. No REA version stated.
- [sickpyramid/ReaFuse](https://github.com/sickpyramid/ReaFuse): built on REA. Version not confirmed as stated.
- [Sage-is/CleanRoom](https://github.com/Sage-is/CleanRoom): a clean-room Python reimplementation of REA's analysis surface. Version not stated.
- [N0zoM1z0/dx-ball](https://github.com/N0zoM1z0/dx-ball): a reconstruction of DX-Ball, linked from REA's showcases. Version not stated.
- [Zfinix/eleven](https://github.com/Zfinix/eleven): a macOS app that analyses with REA. Its README cites "REA 6.x", and its install script is fetched from the project's own repository, which needs a check.

## Inclusion rules

An entry must:

- use REA in a way a reader can reproduce, or be a substantive original writeup;
- state the REA version it was run against;
- state its limitations;
- not copy another project's protected code or assets, in line with the upstream [DISCLAIMER](https://github.com/morluto/rea/blob/main/DISCLAIMER.md);
- not ask readers to run unverified installers.

Mirrors, verbatim or lightly edited copies of the upstream README, download pages that are not the upstream release, and projects whose stated purpose is to defeat REA are excluded.

## Submitting a project

To add a project, follow [CONTRIBUTING.md](CONTRIBUTING.md).

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
