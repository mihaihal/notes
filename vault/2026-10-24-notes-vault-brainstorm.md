---
title: Notes vault: brainstorm and design decisions
source: conversation
date: 2026-10-24
tags: notes-vault, meta
---

A brainstorm of this repo: a local vault where Claude writes notes from transcripts and conversations, and the owner reads them in a browser.

## Takeaways

- Plain HTML and JavaScript: no React, container, server or database.
- Notes are Markdown files in `vault/`; `build.py` bundles them into `notes.js`.
- Two layers per note: a skimmable glance first, full writeup behind a click.
- Source link and date show in the glance header.
- No transcript tools installed for now; the owner hands over a link or pastes text.
- `marked` is approved as the Markdown renderer.
- Git is the owner's job; Claude never changes git state.

## Full writeup

### What it is
A personal, local-only notes vault. Claude writes notes from podcast transcripts, YouTube transcripts and conversations with Claude. The owner opens `index.html` from disk, searches, skims the takeaways and expands the full writeup when wanted.

### Decisions and why
Owner's calls:
- Plain HTML and JS, with a small `build.py` run after each saved note. Nothing has to be started to read notes.
- Glance first, full writeup on click, so a note is skimmable in about a minute.
- `marked` for Markdown rendering, vendored.
- Git handled by the owner only.

Claude's calls:
- `vault/` as folder name (avoids `notes/notes`), `sources/` for raw transcripts.
- `notes.js` generated and kept in the tree, so a fresh checkout works without a build.
- Front matter parsed by hand, no YAML library.
- Substring search where every term must match; the full writeup auto-expands when a hit lives only there.
- `/` focuses search; hash routing keeps the selected note across reloads.

### What was deferred
Transcript fetching. The machine has Python 3.14 and Node 26 only; `yt-dlp`, Whisper and `ffmpeg` are not installed, to be revisited later. Meanwhile Claude uses its own web tools or the owner pastes the transcript.

### Where the docs live
- Spec: `docs/superpowers/specs/2026-10-23-notes-vault-design.md`
- Plan: `docs/superpowers/plans/2026-10-24-notes-vault.md`
- Lessons: `claude-config/lessons.md`
