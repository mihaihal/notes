import argparse
import json
import pathlib
import re
import sys


class NoteError(Exception):
    """Raised for a malformed note; message always starts with the note's path."""


def parse_front_matter(text, path):
    lines = text.splitlines()
    if not lines or lines[0].rstrip() != "---":
        raise NoteError(f"{path}: missing opening '---' front matter fence")
    end = None
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            end = i
            break
    if end is None:
        raise NoteError(f"{path}: missing closing '---' front matter fence")
    meta = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            raise NoteError(f"{path}: front matter line without ':': {line!r}")
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    body = "\n".join(lines[end + 1:])
    return meta, body


def split_body(body):
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^##\s*full writeup\s*$", line.strip(), re.I):
            return "\n".join(lines[:i]).strip(), "\n".join(lines[i:]).strip()
    return body.strip(), ""


def parse_tags(value):
    return [t for t in (p.strip().lower() for p in value.split(",")) if t]


SOURCES = ("podcast", "youtube", "conversation")


def build_note(path):
    path = pathlib.Path(path)
    meta, body = parse_front_matter(path.read_text(encoding="utf-8"), str(path))
    for key in ("title", "source", "date"):
        if not meta.get(key):
            raise NoteError(f"{path}: missing required field '{key}'")
    if meta["source"] not in SOURCES:
        raise NoteError(
            f"{path}: unknown source {meta['source']!r} (expected one of {', '.join(SOURCES)})"
        )
    if path.name[:10] != meta["date"]:
        print(
            f"warning: {path}: file-name date {path.name[:10]} != date {meta['date']}",
            file=sys.stderr,
        )
    glance, full = split_body(body)
    tags = parse_tags(meta.get("tags", ""))
    author = meta.get("author", "")
    raw = " ".join([meta["title"], author, " ".join(tags), glance, full]).lower()
    raw = re.sub(r"<!--.*?-->", " ", raw, flags=re.DOTALL)
    text = " ".join(re.sub(r"[#*_>`\[\]()]", " ", raw).split())
    return {
        "id": path.stem,
        "title": meta["title"],
        "source": meta["source"],
        "url": meta.get("url", ""),
        "date": meta["date"],
        "published": meta.get("published", ""),
        "author": author,
        "tags": tags,
        "glance": glance,
        "full": full,
        "text": text,
    }


def build_all(vault):
    notes = [build_note(p) for p in sorted(pathlib.Path(vault).glob("*.md"))]
    notes.sort(key=lambda n: n["title"])
    notes.sort(key=lambda n: n["date"], reverse=True)
    return notes


def render_js(notes):
    data = json.dumps(notes, ensure_ascii=False, indent=1).replace("</", "<\\/")
    return "window.NOTES = " + data + ";\n"


def main(argv):
    parser = argparse.ArgumentParser(description="Bundle vault/*.md into notes.js")
    parser.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parent))
    args = parser.parse_args(argv)
    root = pathlib.Path(args.root)
    vault = root / "vault"
    if not vault.is_dir():
        print(f"error: vault directory not found: {vault}", file=sys.stderr)
        return 1
    try:
        notes = build_all(vault)
    except NoteError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    for n in notes:
        print(f"{n['date']}  {n['source']}  {n['title']}")
    (root / "notes.js").write_text(render_js(notes), encoding="utf-8")
    print(f"built {len(notes)} notes -> notes.js")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
