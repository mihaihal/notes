import unittest, tempfile, pathlib, io, contextlib
from build import NoteError, parse_front_matter, split_body, parse_tags, build_note, build_all, render_js, main

FM = "---\ntitle: Pricing\nsource: podcast\nurl: https://x.io/e/1\ndate: 2026-10-23\ntags: a, B ,,c\n---\nIntro.\n\n## Takeaways\n- one\n\n## full writeup\n\n### Part\ntext\n"

class ParseFrontMatter(unittest.TestCase):
    def test_splits_on_first_colon_only(self):
        meta, _ = parse_front_matter(FM, "n.md")
        self.assertEqual(meta["url"], "https://x.io/e/1")
    def test_returns_body_after_closing_fence(self):
        _, body = parse_front_matter(FM, "n.md")
        self.assertTrue(body.startswith("Intro."))
    def test_missing_opening_fence_names_file(self):
        with self.assertRaisesRegex(NoteError, r"^vault/bad\.md"):
            parse_front_matter("title: x\n", "vault/bad.md")
    def test_unclosed_fence_names_file(self):
        with self.assertRaisesRegex(NoteError, r"^vault/bad\.md"):
            parse_front_matter("---\ntitle: x\n", "vault/bad.md")

class SplitBody(unittest.TestCase):
    def test_splits_at_full_writeup_case_insensitive(self):
        _, body = parse_front_matter(FM, "n.md")
        glance, full = split_body(body)
        self.assertTrue(glance.endswith("- one"))
        self.assertTrue(full.startswith("## full writeup"))
    def test_no_heading_means_all_glance(self):
        glance, full = split_body("just text\n")
        self.assertEqual((glance, full), ("just text", ""))

class ParseTags(unittest.TestCase):
    def test_normalises(self):
        self.assertEqual(parse_tags("a, B ,,c"), ["a", "b", "c"])
    def test_empty(self):
        self.assertEqual(parse_tags(""), [])

def write(d, name, text):
    p = pathlib.Path(d) / name; p.write_text(text); return p

GOOD = "---\ntitle: {t}\nsource: {s}\ndate: {d}\n---\nglance {t}\n\n## Full writeup\nfull {t}\n"

class BuildNote(unittest.TestCase):
    def test_fields_and_text(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "2026-10-23-a.md", "---\ntitle: A\nsource: youtube\ndate: 2026-10-23\nauthor: Guest\ntags: x\n---\nG\n\n## Full writeup\nF\n")
            n = build_note(p)
        self.assertEqual(n["id"], "2026-10-23-a")
        self.assertEqual(n["tags"], ["x"])
        self.assertEqual(n["url"], "")
        self.assertEqual(n["glance"], "G")
        self.assertTrue(n["full"].startswith("## Full writeup"))
        for word in ("a", "guest", "x", "g", "f"):
            self.assertIn(word, n["text"].split())
    def test_html_comments_excluded_from_text(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "2026-10-23-a.md", "---\ntitle: A\nsource: podcast\ndate: 2026-10-23\n---\nG <!-- secret\nhint --> end\n")
            n = build_note(p)
        self.assertNotIn("secret", n["text"])
        self.assertNotIn("hint", n["text"])
        self.assertIn("end", n["text"].split())
    def test_template_builds_after_filling_placeholders(self):
        tpl = (pathlib.Path(__file__).resolve().parent.parent / "templates" / "note.md").read_text(encoding="utf-8")
        tpl = tpl.replace("date: YYYY-MM-DD", "date: 2026-01-01").replace("title: \n", "title: Template\n", 1)
        with tempfile.TemporaryDirectory() as d:
            n = build_note(write(d, "2026-01-01-template.md", tpl))
        self.assertEqual(n["source"], "podcast")
        self.assertEqual(n["tags"], ["tag-one", "tag-two"])
    def test_missing_required_field_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "2026-10-23-a.md", "---\ntitle: A\nsource: podcast\n---\nbody\n")
            with self.assertRaisesRegex(NoteError, r"date"):
                build_note(p)
    def test_unknown_source_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "2026-10-23-a.md", GOOD.format(t="A", s="blog", d="2026-10-23"))
            with self.assertRaisesRegex(NoteError, r"source"):
                build_note(p)
    def test_date_mismatch_warns_only(self):
        with tempfile.TemporaryDirectory() as d:
            p = write(d, "2026-01-01-a.md", GOOD.format(t="A", s="podcast", d="2026-10-23"))
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                build_note(p)
        self.assertIn("warning", err.getvalue())

class BuildAll(unittest.TestCase):
    def test_sorted_date_desc_then_title(self):
        with tempfile.TemporaryDirectory() as d:
            write(d, "2026-10-01-b.md", GOOD.format(t="B", s="podcast", d="2026-10-01"))
            write(d, "2026-10-02-z.md", GOOD.format(t="Z", s="podcast", d="2026-10-02"))
            write(d, "2026-10-02-a.md", GOOD.format(t="A", s="podcast", d="2026-10-02"))
            ids = [n["id"] for n in build_all(pathlib.Path(d))]
        self.assertEqual(ids, ["2026-10-02-a", "2026-10-02-z", "2026-10-01-b"])
    def test_empty_vault(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(build_all(pathlib.Path(d)), [])

class RenderJs(unittest.TestCase):
    def test_escapes_script_close(self):
        js = render_js([{"full": "a </script> b"}])
        self.assertNotIn("</script>", js)
        self.assertIn("<\\/script>", js)
        self.assertTrue(js.startswith("window.NOTES = "))
    def test_empty(self):
        self.assertEqual(render_js([]), "window.NOTES = [];\n")

class Main(unittest.TestCase):
    def test_bad_note_leaves_output_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d); (root / "vault").mkdir()
            write(root / "vault", "2026-10-23-a.md", "no front matter\n")
            out = root / "notes.js"; out.write_text("OLD")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                code = main(["--root", str(root)])
            self.assertEqual(code, 1)
            self.assertEqual(out.read_text(), "OLD")
            self.assertIn("error:", err.getvalue())
    def test_writes_output(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d); (root / "vault").mkdir()
            write(root / "vault", "2026-10-23-a.md", GOOD.format(t="A", s="podcast", d="2026-10-23"))
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(["--root", str(root)])
            self.assertEqual(code, 0)
            self.assertTrue((root / "notes.js").read_text().startswith("window.NOTES = ["))
