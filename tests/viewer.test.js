// tests/viewer.test.js
const test = require("node:test");
const assert = require("node:assert/strict");
const V = require("../viewer.js");

const n = (id, title, tags, glance, full, author = "") => ({ id, title, tags, glance, full, author, source: "podcast",
  text: [title, author, tags.join(" "), glance, full].join(" ").toLowerCase() });
const A = n("a", "Alpha", ["x"], "glance one", "## Full writeup deep");
const B = n("b", "Beta", ["y"], "glance two", "");
B.source = "youtube";

test("parseQuery drops whitespace-only", () => assert.deepEqual(V.parseQuery("  \t "), []));
test("parseQuery lowercases and splits", () => assert.deepEqual(V.parseQuery(" Deep  ONE"), ["deep", "one"]));
test("filterNotes empty terms returns all", () => assert.deepEqual(V.filterNotes([A, B], { terms: [], source: null, tag: null }), [A, B]));
test("filterNotes requires every term", () => {
  assert.deepEqual(V.filterNotes([A, B], { terms: ["glance", "deep"], source: null, tag: null }), [A]);
  assert.deepEqual(V.filterNotes([A, B], { terms: ["glance", "zzz"], source: null, tag: null }), []);
});
test("filterNotes by source and tag", () => {
  assert.deepEqual(V.filterNotes([A, B], { terms: [], source: "youtube", tag: null }), [B]);
  assert.deepEqual(V.filterNotes([A, B], { terms: [], source: null, tag: "x" }), [A]);
});
test("shouldAutoExpand only when a term lives solely in full", () => {
  assert.equal(V.shouldAutoExpand(A, ["deep"]), true);
  assert.equal(V.shouldAutoExpand(A, ["glance"]), false);
  assert.equal(V.shouldAutoExpand(A, []), false);
});
test("shouldAutoExpand ignores terms that hit the visible author", () => {
  const J = n("j", "Jay", ["z"], "g", "## Full writeup body", "Jane Guest");
  assert.equal(V.shouldAutoExpand(J, ["jane"]), false);
});
test("parseQuery strips the characters build.py strips", () => assert.deepEqual(V.parseQuery("(14:32) #42"), ["14:32", "42"]));
test("pickSelected falls back to first visible", () => {
  assert.equal(V.pickSelected([A, B], "b"), B);
  assert.equal(V.pickSelected([A, B], "nope"), A);
  assert.equal(V.pickSelected([], "a"), null);
});
test("allTags unique sorted", () => assert.deepEqual(V.allTags([A, B, A]), ["x", "y"]));
