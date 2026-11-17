---
name: sandbox-ship
description: Ship a change to an app in this sandbox repo so it is live on GitHub Pages. Use whenever an app or the homepage was added or changed, or the user says to ship, merge, push live or deploy. Covers the branch dance, the PR, the squash merge (including the 405 conflict case) and confirming the live site.
---

# Ship a change live

The site is GitHub Pages served from the **default branch** (`claude/epic-pasteur-fsjjc8`). A pushed feature branch is not live. Every change goes: commit, PR into the default branch, merge, confirm the deploy. The live site is https://kristynagottvald.github.io/sandbox/.

Develop on the branch the session was given (for example `claude/<adjective>-<name>-<id>`). Never push to any other branch. Do not create a PR unless this repo's `CLAUDE.md` or the user asks for one; here `CLAUDE.md` does ask.

## Steps

1. **Start from the current default branch.** The branch you were given is usually already squash-merged and behind.
   ```bash
   git fetch -q origin claude/epic-pasteur-fsjjc8
   git checkout -q -B <your-branch> origin/claude/epic-pasteur-fsjjc8
   ```
2. **Make the change and check it** (see the `sandbox-visual-check` skill). If the app's look changed, re-record its clip: `NODE_PATH=$(npm root -g) node tools/record-clips.js <app>`.
3. **Commit** only the files you changed. End the message with the attribution lines from the session's system reminder (`Co-Authored-By` and `Claude-Session`).
4. **Make the push a fast-forward without force.** After a squash-merge the remote branch has old commits, so a plain push is rejected, and force-pushing is blocked. Merge the old tip in with the `ours` strategy, which keeps your tree:
   ```bash
   git fetch -q origin <your-branch>
   git merge -q -s ours origin/<your-branch> -m "Merge earlier branch history (already squash-merged)"   # plus the attribution lines
   git push -q origin <your-branch>
   ```
   Commit first, then merge, then push. Check `git status` shows nothing uncommitted before the merge.
5. **Open the PR** with the GitHub MCP tool `create_pull_request` (owner `kristynagottvald`, repo `sandbox`, base `claude/epic-pasteur-fsjjc8`, head your branch). Describe what changed in a few lines and end the body with the attribution lines from the system reminder. Use markdown links for PRs, never a bare `#123`.
6. **Squash-merge** with `merge_pull_request` (`merge_method: squash`).
   - **405 "Pull Request has merge conflicts"** has two causes. (a) GitHub has not recomputed mergeability yet: wait about 20 seconds and retry. (b) The default branch really moved. Run `git fetch origin claude/epic-pasteur-fsjjc8`, then `git rev-list --count HEAD..origin/claude/epic-pasteur-fsjjc8`. If it is above 0, `git merge origin/claude/epic-pasteur-fsjjc8`, resolve, commit, push, retry.
   - **Usual conflict shape:** `apps.json` and `tools/record-clips.js`, where both sides added an entry at the top. Take the default branch's version (`git checkout --theirs <file>`) and re-insert your entry. For `apps.json` do it with a short Python script that loads the JSON, inserts your object at index 0 and dumps it back. For `record-clips.js` replace your own entry block in their file. Run `node --check tools/record-clips.js` and `node -e "require('./apps.json')"` before committing.
7. **Confirm it is live.** The Pages build takes a minute or two. Poll the live page for a string that only exists in the new version:
   ```bash
   B=https://kristynagottvald.github.io/sandbox/<app>/
   for i in $(seq 1 24); do curl -s $B | grep -q '<marker string>' && echo live && break; sleep 10; done
   ```
   For a new app also check that `<app>/thumb.webp`, `<app>/thumb.png` and any asset folders return 200, and that `curl -s https://kristynagottvald.github.io/sandbox/apps.json | grep -c <app-id>` is at least 1. `mcp__github__actions_list` with `list_workflow_runs` shows the "pages build and deployment" run if you need the status.
8. Tell the user it is live, with the link, and what you did not check.

## Gotchas

- Do not `sleep` more than a few seconds in a chained command; use the polling loop above.
- Do not use `../` paths in shell commands: a safety check once refused the whole command. Write helper scripts with the file tool instead.
- Several requests in a row each get their own commit, PR and merge. Do not batch unmerged work across PRs.
- If a merge succeeded but the marker never appears, check the workflow run before assuming the change was wrong.
