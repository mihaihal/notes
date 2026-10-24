# Tasks

## 2026-10-24 — Notes vault v1
Plan: docs/superpowers/plans/2026-10-24-notes-vault.md
Spec: docs/superpowers/specs/2026-10-23-notes-vault-design.md

- [x] Task 1: project skeleton
- [x] Task 2: front matter and body parsing (build.py)
- [x] Task 3: build notes.js
- [x] Task 4: viewer pure logic (viewer.js, Node tests)
- [x] Task 5: viewer page (index.html, style.css, vendored marked 15.0.7)
- [x] Task 6: note template, first note, CLAUDE.md
- [x] Final review + one fix wave (template hints, HTML comments in search text, scroll reset, author in auto-expand, query normalisation, Escape idle, pycache, unused import)
- [x] Owner: open index.html in a browser and check the list below (confirmed 2026-10-24)
- [ ] Owner: commit (git is owner-only)

### Review
- Tests: `python3 -B -m unittest tests.test_build -v` → 20 OK; `node --test tests/viewer.test.js` → 10 pass.
- Plan defects found during execution: one test had assertions outside its temp-dir block; `node --test tests/` rejected on Node 26; spec's note-format example put `# hints` inside front-matter values. All fixed.
- Deferred minors (not blocking): non-UTF-8 note gives a traceback; `## Full writeup` inside a code fence would split; BOM before `---` not tolerated; notes.js write not atomic; date format not validated; rows not keyboard-focusable; active row not scrolled into view; typing collapses a hand-opened writeup; raw HTML in Markdown rendered as-is.

### Manual browser check (owner)
1. Double-click index.html: one note listed, glance renders, header shows badge, date, tags.
2. Click "Show full writeup" → expands; click again → collapses.
3. Type a word that appears only in the full writeup (e.g. "deferred") → note stays listed and the writeup auto-opens.
4. Type gibberish → "No notes match". Press Escape → list returns.
5. Press `/` → search box focused. Check dark mode if your system uses it.
