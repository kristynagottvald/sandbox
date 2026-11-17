---
name: ship-sandbox-app
description: Add or change an app in the sandbox repo (single-file index.html apps under kristynagottvald/sandbox) and get it live on the GitHub Pages site. Use whenever an app folder, apps.json, tools/record-clips.js or a homepage clip changes, and for any "ship it / make it live" request in that repo. Covers the new-app checklist, recording the homepage clip, the branch-reset ship loop (the repo squash-merges), the PR and merge, and verifying the live site.
---

# Ship a sandbox app

The repo's CLAUDE.md is the source of truth. This skill is the working procedure for it. Read CLAUDE.md first if it changed.

## Facts about the repo

- One folder per app: `index.html` (single file, no build step), `thumb.webp` (6 s looping clip, 960x540) and `thumb.png` (the clip's first frame).
- The homepage draws its tiles from `/apps.json`, newest first.
- Pages is served from the **default branch** (`claude/epic-pasteur-fsjjc8` at the time of writing; confirm in CLAUDE.md). Pushing a feature branch is not enough: the change must be merged and the live site checked. Live site: https://kristynagottvald.github.io/sandbox/
- Merges are **squash merges**. A feature branch that was already squash-merged will conflict if you rebase it. Always use the reset approach below.

## New app checklist

1. Folder `<app>/index.html` with the `<nav class="back">` "Sandbox / Back to all projects / Title" bar linking to `../` (copy it from an existing app).
2. Entry at the **top** of `apps.json`: `id`, `title`, `category` (reuse an existing category), `url` (`<app>/`), `thumbnail` (`<app>/thumb.png`), `preview` (`<app>/thumb.webp`), `alt` (describe what the tile shows).
3. Row in the `APPS` table of `tools/record-clips.js`, then record the clip (next section).
4. Ship (below) and verify live.

Changing an existing app: re-record the clip whenever its look changes (a changed default view, a new panel section, new colours). Behaviour-only fixes that do not change the first screen do not need a new clip.

## Recording the homepage clip

```bash
NODE_PATH=$(npm root -g) node tools/record-clips.js <app>      # needs playwright and ffmpeg with libwebp, see tools/README.md
```

- Table entry: `vp: [1280, 769]`, `crop: [0, 49, 1280, 720]` (the 49px nav is cropped off), optional `setup(page)`, `ready` ms, and `run(page)`: a timeline of actions in ms after the page is ready.
- **The clip's first frame is also its loop point, so it must show the finished, default state.** The video lags the page, so a first action at ~700 ms can already show up in frame 0. Park the app in its finished state in `setup` (expose a tiny `window.xx.seek(n)` / `play({speed, loop:false})` hook on the page if needed) and start the first action around 1400 ms.
- Drive the app the way a visitor would (click buttons by selector, e.g. `domClick(p, '#themes .opt:nth-child(3)')`). Selectors break when you reorder or remove buttons, so update the table in the same change.
- Always look at the result: open the WebP with PIL, tile frames 0, 10, 20, 30, 40, last into one PNG and view it. Check frame 0 is the finished card and the last frames fade back to it.

## Visual QA before shipping

Write a throwaway Playwright script (scratchpad, not the repo) that loads `file:///.../<app>/index.html`, sets each state (themes x ratios x options), screenshots, and tile the shots into one contact sheet with PIL. Look at the sheet. Fixing a layout "by feel" without looking is how regressions ship. When changing generated JS with scripted edits, use a replace helper that asserts the old text occurs exactly once, and never put a `//` comment at the end of a line that continues with code.

## Ship loop

Work on the feature branch named in the session instructions. When the change is ready:

```bash
.claude/skills/ship-sandbox-app/scripts/ship.sh "Short message

<attribution trailers from the session>" <app> apps.json tools/record-clips.js
```

This commits, cuts the branch fresh from the default branch, copies only the given paths onto it, and force-pushes (`--dry-run` shows the steps). Only list paths you changed; list nothing else.

Then with the GitHub MCP tools (the `gh` CLI is not available for PRs):
1. `create_pull_request` into the default branch. Mirror any PR template. End the body with the attribution lines from the session. Say what changed in two or three bullets.
2. `merge_pull_request` with `merge_method: "squash"`. If it answers "merge conflicts", the branch was not reset onto the default branch: run `ship.sh` again.

Verify live (never claim it is live before this passes):

```bash
.claude/skills/ship-sandbox-app/scripts/wait-live.sh https://kristynagottvald.github.io/sandbox/<app>/ '<a string you just added>'
curl -s -o /dev/null -w '%{http_code}\n' https://kristynagottvald.github.io/sandbox/<app>/thumb.webp
```

Check that the homepage tile entry is in the live `apps.json` too for new apps.

## Reporting

Say what is merged, with PR links as `[owner/repo#N](url)`, what you verified live and how, and what you did not verify (for example "I did not open the live page in a browser"). Never write a bare `#123`.

## Traps seen before

- Images pasted into chat are not files on disk. Look in the session's images folder; if the file is missing, say so and look for the original (see the `cutout-product-image` skill) instead of faking it.
- The pasted `Co-Authored-By` / `Claude-Session` lines belong at the end of every commit message the session reminder names.
- Do not poll with a hand-written `sleep` loop in a tool call; use `wait-live.sh`.
- Do not skip, disable or quarantine a check to get a green result.
