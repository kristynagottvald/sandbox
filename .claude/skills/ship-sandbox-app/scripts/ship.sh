#!/usr/bin/env bash
# Put the changes under the given paths onto a fresh branch cut from the default branch, then push it.
# Needed because the repo squash-merges: after a squash merge the old feature branch no longer rebases cleanly.
#
#   ship.sh [--dry-run] "<commit message incl. attribution trailers>" path [path...]
#
# Run from the repo root on the feature branch, with the changes already in the working tree.
# Open the PR and merge it with the GitHub MCP tools afterwards (create_pull_request, merge_pull_request with squash).
set -euo pipefail
DRY=0; [ "${1:-}" = "--dry-run" ] && { DRY=1; shift; }
MSG="${1:?commit message}"; shift; [ "$#" -ge 1 ] || { echo "give at least one path"; exit 1; }
DEFAULT="${DEFAULT_BRANCH:-$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##' || true)}"
DEFAULT="${DEFAULT:-claude/epic-pasteur-fsjjc8}"            # the Pages branch named in CLAUDE.md
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
[ "$BRANCH" != "$DEFAULT" ] || { echo "you are on the default branch ($DEFAULT); switch to the feature branch first"; exit 1; }
run() { echo "+ $*"; [ "$DRY" = 1 ] || "$@"; }
run git add -A -- "$@"
if [ "$DRY" = 1 ]; then echo "+ git commit -m <msg>   (then remember the commit)"; C=HEAD; else git commit -q -m "$MSG"; C="$(git rev-parse HEAD)"; fi
run git fetch -q origin "$DEFAULT"
run git checkout -q -B "$BRANCH" "origin/$DEFAULT"
run git checkout "$C" -- "$@"
[ "$DRY" = 1 ] && echo "+ git commit -m <msg>" || git commit -q -m "$MSG"
run git push -f -u origin "$BRANCH"
echo "pushed $BRANCH on top of $DEFAULT; now open the PR into $DEFAULT and squash-merge it"
