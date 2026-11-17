---
name: ship-to-pages
description: Get sandbox changes live on GitHub Pages: commit, push the feature branch, PR into the default branch, merge, handle the squash-merge conflict, and verify the deploy on the live site. Use after any new or changed app, or when the user says to ship, publish or make it live.
---

# Ship to GitHub Pages

Live site: https://kristynagottvald.github.io/sandbox/ , served from the default branch (`claude/epic-pasteur-fsjjc8`). Pushing a feature branch alone is not live.

1. Commit on the session branch with the attribution lines from the session's system reminder. Push: `git push -u origin <branch>`.
2. Open a PR (GitHub MCP `create_pull_request`) into the default branch. Mirror any PR template; end the body with the attribution lines.
3. Merge with `merge_pull_request`, `merge_method: squash`.
4. **If the merge says "merge conflicts"** there are two causes. (a) GitHub has not recomputed mergeability yet: wait ~20s and retry. (b) The default branch moved, or the session branch was already squash-merged earlier so its old commits conflict. Never force-push (it is blocked here). Instead:
   - Start each new piece of work from the default branch: `git fetch origin <default> && git checkout -B <branch> origin/<default>`, make and commit the change, then make the push a fast-forward by merging the old remote tip in with the `ours` strategy (it keeps your tree): `git fetch origin <branch> && git merge -s ours origin/<branch> -m "Merge earlier branch history (already squash-merged)"` (add the attribution lines), then `git push origin <branch>`. Commit before merging.
   - If the default branch moved while the PR was open: `git fetch origin <default>`, `git merge origin/<default>`, resolve, push, retry the merge. The usual conflicts are `apps.json` and `tools/record-clips.js`, where both sides added an entry at the top: take the default branch's file (`git checkout --theirs <file>`) and re-insert your entry (for `apps.json` with a short Python script that loads the JSON, inserts your object at index 0 and dumps it; check with `node -e "require('./apps.json')"` and `node --check tools/record-clips.js`).
5. **Verify the deploy.** Poll the live page for a string unique to the change until it appears (deploys take ~30-60s):
   ```bash
   for i in $(seq 1 24); do curl -s <live-url> | grep -c '<marker>' && break; sleep 15; done
   ```
   Also check `actions_list` `list_workflow_runs` for the "pages build and deployment" run being `success`.
6. For a new app also confirm `apps.json` on the live site contains it and the `thumb.webp` URL returns 200.
7. Report the PR link and what was confirmed live. Say so plainly if something could not be verified.
