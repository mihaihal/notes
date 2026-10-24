// Pure viewer logic. Loads as a classic <script> (file://) and as a CommonJS module.

function parseQuery(q) {
  return String(q).toLowerCase().replace(/[#*_>`\[\]()]/g, " ").split(/\s+/).filter(Boolean);
}

function filterNotes(notes, { terms, source, tag }) {
  return notes.filter((note) =>
    (!source || note.source === source) &&
    (!tag || note.tags.includes(tag)) &&
    terms.every((t) => note.text.includes(t)));
}

function shouldAutoExpand(note, terms) {
  if (terms.length === 0) return false;
  if (!terms.every((t) => note.text.includes(t))) return false;
  const head = (note.title + " " + note.tags.join(" ") + " " + (note.author || "") + " " + note.glance).toLowerCase();
  return terms.some((t) => !head.includes(t));
}

function pickSelected(visible, hashId) {
  return visible.find((note) => note.id === hashId) || visible[0] || null;
}

function allTags(notes) {
  return [...new Set(notes.flatMap((note) => note.tags))].sort();
}

if (typeof document !== "undefined") {
  const state = { query: "", source: null, tag: null };
  let lastId = null;
  const $ = (id) => document.getElementById(id);
  const md = (src) => (marked.parse ? marked.parse(src) : marked.marked.parse(src));

  function el(tag, props, ...children) {
    const node = document.createElement(tag);
    Object.assign(node, props);
    for (const c of children) if (c != null) node.append(c);
    return node;
  }

  function badge(source) {
    const b = el("span", { className: "badge", textContent: source });
    b.dataset.source = source;
    return b;
  }

  function tagList(tags) {
    return tags.map((t) => el("span", { className: "tag", textContent: t }));
  }

  function renderNote(note, terms) {
    const main = $("note");
    main.replaceChildren();
    const meta = el("div", { className: "meta" }, badge(note.source), el("span", { textContent: note.date }));
    if (note.published) meta.append(el("span", { textContent: "published " + note.published }));
    if (note.author) meta.append(el("span", { textContent: note.author }));
    meta.append(...tagList(note.tags));
    if (note.url) meta.append(el("a", { href: note.url, target: "_blank", rel: "noopener", textContent: "Source" }));
    main.append(el("header", {}, el("h1", { textContent: note.title }), meta));
    main.append(el("div", { className: "glance", innerHTML: md(note.glance) }));
    if (note.full) {
      const open = shouldAutoExpand(note, terms);
      const toggle = el("button", { id: "toggle", textContent: open ? "Hide full writeup" : "Show full writeup" });
      const full = el("section", { id: "full", hidden: !open, innerHTML: md(note.full) });
      toggle.addEventListener("click", () => {
        full.hidden = !full.hidden;
        toggle.textContent = full.hidden ? "Show full writeup" : "Hide full writeup";
      });
      main.append(toggle, full);
    }
  }

  function render() {
    const notes = window.NOTES || [];
    const terms = parseQuery(state.query);
    const visible = filterNotes(notes, { terms, source: state.source, tag: state.tag });
    const selected = pickSelected(visible, location.hash.slice(1));

    for (const b of $("sources").querySelectorAll("button")) {
      b.classList.toggle("active", (b.dataset.source || null) === state.source);
    }

    $("tags").replaceChildren(...allTags(notes).map((t) => {
      const b = el("button", { textContent: t, className: t === state.tag ? "active" : "" });
      b.addEventListener("click", () => {
        state.tag = state.tag === t ? null : t;
        render();
      });
      return b;
    }));

    $("list").replaceChildren(...visible.map((note) => {
      const li = el("li", { className: "row" + (selected && note.id === selected.id ? " active" : "") },
        el("div", { className: "row-title", textContent: note.title }),
        el("div", { className: "meta" }, badge(note.source), el("span", { textContent: note.date }), ...tagList(note.tags)));
      li.addEventListener("click", () => { location.hash = "#" + note.id; });
      return li;
    }));

    if (selected) {
      renderNote(selected, terms);
      if (selected.id !== lastId) $("note").scrollTop = 0;
      lastId = selected.id;
    }
    else $("note").replaceChildren(el("p", { className: "empty", textContent: "No notes match" }));
  }

  const search = $("search");
  search.addEventListener("input", () => {
    state.query = search.value;
    render();
  });

  for (const b of $("sources").querySelectorAll("button")) {
    b.addEventListener("click", () => {
      state.source = b.dataset.source || null;
      render();
    });
  }

  document.addEventListener("keydown", (e) => {
    const t = e.target;
    const typing = t instanceof HTMLElement && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName));
    if (e.key === "/" && !typing) {
      e.preventDefault();
      search.focus();
    } else if (e.key === "Escape") {
      if (state.query === "" && document.activeElement !== search) return;
      state.query = "";
      search.value = "";
      search.blur();
      render();
    }
  });

  window.addEventListener("hashchange", render);
  render();
}

if (typeof module !== "undefined") module.exports = { parseQuery, filterNotes, shouldAutoExpand, pickSelected, allTags };
