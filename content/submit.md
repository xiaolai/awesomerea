## Submit a project

1. **Fork** this repository and create a branch from `main`.
2. **Add one line** to the right section in `content/list.md`, or to **Pending verification** in `content/pending.md`:
   - Cases and writeups, Tools and integrations, or Resources.
   - Format: `- [owner/name](https://github.com/owner/name): one-sentence description. REA x.y.z.`
   - If the project does not state an REA version, add it to `content/pending.md` instead, and say what is missing.
3. **Open a pull request** against `main`. Title it `Add owner/name` (or `Add owner/name to pending verification`).
4. **Fill in the checklist** in the pull request description:
   - [ ] The project uses REA, and a reader can reproduce its steps or it is a substantive writeup.
   - [ ] The REA version is stated in the project's own README, and the version in your entry matches it.
   - [ ] The project's README states its limitations.
   - [ ] It does not copy protected code or assets, and it is not a mirror of the upstream README.
   - [ ] Its install steps come from the official upstream release or from a source you have checked.
   - [ ] It is not a download page, and it does not present REA as a target to defeat.

A maintainer checks each item before merging. A pull request that leaves an item unchecked, or that adds more than one project, will be asked to split or revise. Do not edit `data/exclusions.json` in your pull request; if you think an excluded repository should be reconsidered, say so in the description.

After editing `content/`, run `python3 tools/build_site.py` and commit the regenerated `docs/` with your change. The site is built from these files, so a pull request that edits only `docs/` will not be accepted.
