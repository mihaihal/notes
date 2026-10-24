# Lessons

Patterns learned from corrections. Read at the start of each session.

## 2026-10-23 — Git is the owner's
Never run git commands that change state (init, add, commit, checkout,
branch, stash, reset, push). Read-only git (status, log, diff, show) is fine.
Do not propose "initialise the repo" as a step; leave `.gitignore` creation
as a file write and let the owner commit.
