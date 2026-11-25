---
name: sandbox-ship-app
description: Add, change or rename an app in the sandbox repo and get it live on GitHub Pages. Use whenever an app folder (index.html + thumb.webp + thumb.png) is created, edited or renamed, or when a homepage tile, clip or Pages deploy is involved.
---

# Ship a sandbox app

The repo's `CLAUDE.md` is the source of truth. This is the checklist that gets an app all the way to the live site (https://kristynagottvald.github.io/sandbox/). The default branch is `claude/epic-pasteur-fsjjc8`.

## 1. The app
- One folder, one self-contained `index.html` (no build step). Supporting assets may sit beside it (`assets/`); keep images small (webp, about 256px for thumbnails inside a page).
- Include the shared 72px project bar: `<nav class="back">` with SANDBOX / PROJECT NAME linking to `../` and any app controls in a `<div>` on the right. Copy the markup, base rules and `sandbox project bar` override block from an existing app (e.g. `nlp-diagram/index.html`).

## 2. Homepage tile
- Add an entry at the **top** of `apps.json` (newest first): `id`, `title`, `category` (Motion or Tools), `url` (`<folder>/`), `thumbnail` (`<folder>/thumb.png`), `preview` (`<folder>/thumb.webp`), `alt` (describe what the clip shows).
- Add a row to the `APPS` table in `tools/record-clips.js` (viewport `[1280, 769]`, crop `[0, 49, 1280, 720]`, `run(page)` timeline). See `tools/README.md` for the options.
- Run it: `NODE_PATH=$(npm root -g) node tools/record-clips.js <folder>`. Read `thumb.png` to check the first frame. Re-record whenever the look changes.
- Add the app title to the README's category list.

## 3. Rename an app
`git mv old new`, then update: `apps.json` (id, title, url, thumbnail, preview), the page `<title>` and nav `<b>`, README, and the key in `tools/record-clips.js`. Tell the user the old URL now 404s (offer a redirect page if they want one).

## 4. Release
1. Commit on the session branch, `git push -u origin <branch>`.
2. Open a PR into `claude/epic-pasteur-fsjjc8` (GitHub MCP `create_pull_request`), then `merge_pull_request` with `squash`.
3. Verify on the live site, not in the Actions list (it lags): poll with `curl` until `<url>/<folder>/` returns 200, `apps.json` contains the new id, and `thumb.webp`, `thumb.png` and assets return 200. Pages takes about 30-60 s.

## Git gotchas seen in practice
- **`apps.json` conflicts** are routine (other sessions add tiles). Keep both entries, newest first; check with `python3 -c "import json;json.load(open('apps.json'))"`.
- **"unrelated histories"** means the shallow clone lacks the base: `git fetch --depth=200 origin claude/epic-pasteur-fsjjc8`, then retry (deepen further, then `--unshallow`, if still needed).
- **Never force-push.** It gets blocked and is unnecessary. If the branch was already squash-merged, merge the default branch in, take the default branch's side (`git checkout --theirs`) for files that conflict only because of the earlier squash, and re-apply just the new change.
- Squash-merged work shows up on the default branch as one commit; later edits by other sessions may already have changed your files. Read before overwriting.
