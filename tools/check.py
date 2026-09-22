#!/usr/bin/env python3
"""Structural checker for The Understudy.

Validates the mechanical half of the brief's definition of done — the part
that is boring to re-verify by hand on every page of every book, and exactly
the class of error hand-checking misses.

This is NOT a build step. It reads what is committed and reports; it never
writes, and nothing has to run before the site is served. The site is plain
static HTML and works with this script deleted.

Standard library only. Run with:

    uv run tools/check.py
    python3 tools/check.py -v            # per-file detail
    python3 tools/check.py --only links  # one check
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urldefrag

ROOT = Path(__file__).resolve().parent.parent
LOG = logging.getLogger("check")

# Sections every part page must carry, in the brief's order.
REQUIRED_SECTIONS = ["where", "read", "voice", "ledger", "notes", "carry"]

# What each kind's #read must contain: ("class", token) or ("tag", name),
# mapped to a human name. These MUST match real markup rather than a bare
# substring -- prose that merely mentions "joints" is not a joint map, and an
# earlier version of this check was fooled by exactly that.
KIND_REQUIREMENTS = {
    "claim": [(("class", "joints"), "the joint map"),
              (("class", "case-walk"), "a case walked"),
              (("class", "support"), "the support ledger")],
    "mechanism": [(("class", "ratchet"), "the ratchet"),
                  (("class", "trace"), "the trace"),
                  (("class", "costs"), "the cost sheet"),
                  (("tag", "svg"), "a figure")],
    "terrain": [(("class", "axes"), "the axes"),
                (("class", "placements"), "items placed")],
}


def has_markup(scope: str, kind_of: str, name: str) -> bool:
    """True when `scope` contains an element carrying that class, or that tag.

    The class attribute is split on whitespace and compared token by token, so
    class="case-walk contrast" counts for "case-walk" while prose merely
    mentioning the word does not. An earlier substring version of this check
    was fooled by exactly that, and passed a page whose joint map had been
    renamed away.
    """
    if kind_of == "tag":
        return re.search(rf"<{re.escape(name)}\b", scope) is not None
    return any(name in m.group(1).split()
               for m in re.finditer(r'class="([^"]*)"', scope))


# The theme switch. assets/theme.js must load synchronously in <head> on every
# page (anything later paints a frame in the wrong theme), and every page
# carries exactly one switch in its site header. See ARCHITECTURE.md §2.
THEME_JS = ROOT / "assets" / "theme.js"
TOGGLE_ATTRS = {"type": "button", "role": "switch"}
TOGGLE_REQUIRED = ("aria-checked", "aria-label", "hidden")

# The dark token values are written twice in style.css, because plain CSS
# cannot OR a media query with a selector. Neither block contains a brace, so
# a non-greedy match to the first "}" captures exactly its declarations.
DARK_BLOCKS = {
    "OS dark (media query)": re.compile(
        r'@media \(prefers-color-scheme: dark\)\s*\{\s*'
        r':root:where\(:not\(\[data-theme="light"\]\)\)\s*\{(.*?)\}', re.S),
    "chosen dark (data-theme)": re.compile(
        r'^:root:where\(\[data-theme="dark"\]\)\s*\{(.*?)\}', re.S | re.M),
}

# Anything that lets a script reach the network. fetch() also breaks file://,
# which is why the brief forbids it by name.
NETWORK_JS = re.compile(
    r"\bfetch\s*\(|XMLHttpRequest|\bimport\s*\(|sendBeacon|WebSocket|EventSource")


def strip_js_comments(code: str) -> str:
    """Drop /* */ and // comments, so prose about fetch() is not a violation.

    Naive about `//` inside string literals, which can only ever hide code
    from the scan, never invent a match -- acceptable for a site whose one
    script contains no URLs.
    """
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", code, flags=re.S)


def css_declarations(block: str) -> dict[str, str]:
    """Parse `prop: value;` pairs, ignoring comments and whitespace layout."""
    block = re.sub(r"/\*.*?\*/", "", block, flags=re.S)
    decls = {}
    for part in block.split(";"):
        if ":" in part:
            prop, value = part.split(":", 1)
            decls[prop.strip()] = " ".join(value.split())
    return decls


META_REQUIRED = [
    "slug", "title", "author", "year", "domains", "parts", "kinds", "words",
    "reading_minutes", "chapters_covered", "book_still_required",
    "prerequisites", "status", "published", "updated",
]


class Page(HTMLParser):
    """Collects just enough structure to answer the checks below."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: list[tuple[int, str]] = []   # (level, id)
        self.ids: set[str] = set()
        self.links: list[str] = []                  # href values
        self.srcs: list[str] = []                   # src values
        self.lang: str | None = None
        self.has_viewport = False
        self.has_charset = False
        self.title = ""
        self.landmarks: set[str] = set()
        self.kinds: list[str] = []                  # data-kind values
        self.section_ids: set[str] = set()
        self.fn_refs: list[str] = []                # <a href="#fn-..."> targets
        self.fn_backs: list[str] = []               # <a class="fn-back" href="#...">
        self.script_srcs: list[str] = []
        # (attrs, was it inside <head>?) for every <script>
        self.scripts: list[tuple[dict, bool]] = []
        # (tag, attrs, was it inside header.site?) for every .theme-toggle
        self.toggles: list[tuple[str, dict, bool]] = []
        self._in_title = False
        self._in_head = False
        self._in_site_header = False
        self._h_stack: list[int] = []

    def handle_starttag(self, tag: str, attrs_list: list) -> None:
        a = dict(attrs_list)
        if "id" in a and a["id"]:
            self.ids.add(a["id"])
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "meta":
            if a.get("charset"):
                self.has_charset = True
            if a.get("name") == "viewport":
                self.has_viewport = True
        elif tag == "title":
            self._in_title = True
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append((int(tag[1]), a.get("id", "")))
        elif tag == "a":
            href = a.get("href")
            if href:
                self.links.append(href)
                if "fn-back" in (a.get("class") or ""):
                    self.fn_backs.append(href)
                elif href.startswith("#fn-"):
                    self.fn_refs.append(href)
        elif tag in ("img", "link", "source", "iframe", "use", "image"):
            for key in ("src", "href", "srcset", "xlink:href"):
                if a.get(key):
                    self.srcs.append(a[key])
        elif tag == "script":
            self.script_srcs.append(a.get("src", "<inline>"))
            self.scripts.append((a, self._in_head))
            if a.get("src"):
                self.srcs.append(a["src"])   # so check_links resolves it too
        elif tag == "head":
            self._in_head = True
        elif tag in ("main", "header", "footer", "nav", "article", "section", "aside"):
            self.landmarks.add(tag)
            if tag == "section" and a.get("id"):
                self.section_ids.add(a["id"])
            if tag == "header" and "site" in (a.get("class") or "").split():
                self._in_site_header = True
        if a.get("data-kind"):
            self.kinds.append(a["data-kind"])
        if "theme-toggle" in (a.get("class") or "").split():
            self.toggles.append((tag, a, self._in_site_header))

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "head":
            self._in_head = False
        elif tag == "header":
            self._in_site_header = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data.strip()


class Report:
    """Accumulates failures and warnings, grouped by check name."""

    def __init__(self) -> None:
        self.failures: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []
        self.counts: dict[str, int] = {}

    def fail(self, check: str, msg: str) -> None:
        self.failures.append((check, msg))
        LOG.error("%s: %s", check, msg)

    def warn(self, check: str, msg: str) -> None:
        self.warnings.append((check, msg))
        LOG.warning("%s: %s", check, msg)

    def tally(self, check: str, n: int = 1) -> None:
        self.counts[check] = self.counts.get(check, 0) + n


def html_files() -> list[Path]:
    return sorted(
        p for p in ROOT.rglob("*.html")
        if ".git" not in p.parts and "node_modules" not in p.parts
    )


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


# --------------------------------------------------------------------------
# checks
# --------------------------------------------------------------------------

def check_nojekyll(rep: Report) -> None:
    """GitHub Pages skips underscore-prefixed dirs (_template/) without it."""
    if (ROOT / ".nojekyll").is_file():
        rep.tally("nojekyll")
    else:
        rep.fail("nojekyll", ".nojekyll missing from repo root")


def check_links(rep: Report, pages: dict[Path, Page]) -> None:
    """All links relative, all relative targets resolve, all anchors exist."""
    for path, page in pages.items():
        for href in page.links + page.srcs:
            if href.startswith("#"):
                frag = unquote(href[1:])
                if frag and frag not in page.ids:
                    rep.fail("links", f"{rel(path)} -> '{href}' (no such id on page)")
                else:
                    rep.tally("links")
                continue
            if href.startswith("/"):
                rep.fail("links", f"{rel(path)} -> '{href}' (absolute path; must be relative)")
                continue
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href):
                continue  # scheme-bearing; handled by check_network
            target, frag = urldefrag(href)
            if not target:
                continue
            resolved = (path.parent / unquote(target)).resolve()
            if not resolved.exists():
                rep.fail("links", f"{rel(path)} -> '{href}' (target does not exist)")
                continue
            if frag and resolved.suffix == ".html":
                other = pages.get(resolved)
                if other and unquote(frag) not in other.ids:
                    rep.fail("links", f"{rel(path)} -> '{href}' (no such id in target)")
                    continue
            rep.tally("links")


def check_network(rep: Report, pages: dict[Path, Page]) -> None:
    """The site must render fully with the network off."""
    allowed = ("mailto:", "tel:")
    for path, page in pages.items():
        for href in page.links + page.srcs:
            if href.startswith(("http://", "https://", "//")):
                # Outbound links in prose are fine and required (where to buy
                # the book); loading a RESOURCE from the network is not.
                if href in page.srcs:
                    rep.fail("network", f"{rel(path)} loads '{href}' from the network")
                else:
                    rep.tally("network")
            elif re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href) and not href.startswith(allowed):
                rep.warn("network", f"{rel(path)} uses scheme in '{href}'")
        for src in page.script_srcs:
            if src != "<inline>" and src.startswith(("http", "//")):
                rep.fail("network", f"{rel(path)} loads script '{src}' from the network")

    css = ROOT / "assets" / "style.css"
    if css.is_file():
        for m in re.finditer(r"""url\(\s*['"]?([^'")]+)""", css.read_text()):
            u = m.group(1).strip()
            if u.startswith(("http", "//")):
                rep.fail("network", f"assets/style.css references '{u}'")
            elif not u.startswith("data:"):
                if not (css.parent / u).exists():
                    rep.fail("network", f"assets/style.css -> '{u}' (missing file)")
                else:
                    rep.tally("network")
        if "@import" in css.read_text():
            rep.warn("network", "assets/style.css contains @import")

    # JavaScript may only enhance, and may never reach the network.
    for js in sorted((ROOT / "assets").rglob("*.js")):
        m = NETWORK_JS.search(strip_js_comments(js.read_text(encoding="utf-8")))
        if m:
            rep.fail("network", f"{rel(js)} uses '{m.group(0)}' "
                                "(scripts may never reach the network)")
        else:
            rep.tally("network")


def check_structure(rep: Report, pages: dict[Path, Page]) -> None:
    """One <h1> per page; heading levels never skip going down."""
    for path, page in pages.items():
        h1s = [h for h in page.headings if h[0] == 1]
        if len(h1s) != 1:
            rep.fail("structure", f"{rel(path)} has {len(h1s)} <h1> (must be exactly 1)")
        else:
            rep.tally("structure")

        prev = 0
        for level, _ in page.headings:
            if prev and level > prev + 1:
                rep.fail("structure",
                         f"{rel(path)} heading order skips h{prev} -> h{level}")
                break
            prev = level

        # The brief requires an id on every heading — it is what makes a
        # table of contents and any cross-reference possible at all.
        missing_ids = [f"h{lv}" for lv, hid in page.headings if not hid]
        if missing_ids:
            rep.fail("structure",
                     f"{rel(path)} has {len(missing_ids)} heading(s) without an id: "
                     + ", ".join(missing_ids))


def check_a11y(rep: Report, pages: dict[Path, Page]) -> None:
    """lang, charset, viewport, a title, a skip link, and real landmarks."""
    for path, page in pages.items():
        name = rel(path)
        if not page.lang:
            rep.fail("a11y", f"{name} <html> has no lang")
        if not page.has_charset:
            rep.fail("a11y", f"{name} has no <meta charset>")
        if not page.has_viewport:
            rep.fail("a11y", f"{name} has no viewport meta")
        if not page.title:
            rep.fail("a11y", f"{name} has an empty <title>")
        if "main" not in page.landmarks:
            rep.fail("a11y", f"{name} has no <main>")
        if "#main" not in page.links:
            rep.fail("a11y", f"{name} has no skip link to #main")
        if not {"header", "footer"} <= page.landmarks:
            rep.warn("a11y", f"{name} is missing a header or footer landmark")
        rep.tally("a11y")


def check_footnotes(rep: Report, pages: dict[Path, Page]) -> None:
    """Every ref reaches a note, and every note gets back."""
    for path, page in pages.items():
        for href in page.fn_refs:
            fid = href[1:]
            if fid not in page.ids:
                rep.fail("footnotes", f"{rel(path)} ref -> '{href}' has no note")
                continue
            backs = {b[1:] for b in page.fn_backs}
            expected = fid.replace("fn-", "fnref-", 1)
            if expected not in backs:
                rep.fail("footnotes",
                         f"{rel(path)} note '{fid}' has no return link to '{expected}'")
                continue
            if expected not in page.ids:
                rep.fail("footnotes", f"{rel(path)} return link -> '#{expected}' has no target")
                continue
            rep.tally("footnotes")


def check_parts(rep: Report, pages: dict[Path, Page], raw: dict[Path, str]) -> None:
    """Part pages: all six sections, a declared kind, that kind's apparatus."""
    for path, page in pages.items():
        text = raw[path]
        if 'class="part"' not in text or "data-kind" not in text:
            continue
        name = rel(path)
        missing = [s for s in REQUIRED_SECTIONS if s not in page.section_ids]
        if missing:
            rep.fail("parts", f"{name} missing section(s): {', '.join(missing)}")
        else:
            rep.tally("parts")

        for sid in REQUIRED_SECTIONS:
            if sid in page.section_ids:
                m = re.search(rf'<section id="{sid}"[^>]*>(.*?)</section>', text, re.S)
                if m and not re.sub(r"<[^>]+>|\s", "", m.group(1)):
                    rep.fail("parts", f"{name} section #{sid} is empty")

        for kind in page.kinds:
            if kind not in KIND_REQUIREMENTS:
                rep.fail("kinds", f"{name} declares unknown data-kind '{kind}'")
                continue
            read = re.search(r'<section id="read".*?</section>', text, re.S)
            scope = read.group(0) if read else text
            for (kind_of, needle), human in KIND_REQUIREMENTS[kind]:
                if not has_markup(scope, kind_of, needle):
                    rep.fail("kinds", f"{name} is data-kind='{kind}' but has no {human}")
                else:
                    rep.tally("kinds")


def check_theme(rep: Report, pages: dict[Path, Page]) -> None:
    """theme.js in every <head>, one switch per header, dark tokens in sync."""
    for path, page in pages.items():
        name = rel(path)
        before = len(rep.failures)

        loads = [(a, in_head) for a, in_head in page.scripts
                 if a.get("src")
                 and (path.parent / unquote(a["src"])).resolve() == THEME_JS]
        if len(loads) != 1:
            rep.fail("theme", f"{name} loads assets/theme.js {len(loads)} "
                              "time(s) (must be exactly 1)")
        else:
            attrs, in_head = loads[0]
            if not in_head:
                rep.fail("theme", f"{name} loads theme.js outside <head> "
                                  "(the first frame would paint in the wrong theme)")
            if "defer" in attrs or "async" in attrs:
                rep.fail("theme", f"{name} loads theme.js with defer/async "
                                  "(the first frame would paint in the wrong theme)")
            if attrs.get("type") not in (None, "text/javascript"):
                rep.fail("theme", f"{name} loads theme.js as type="
                                  f"'{attrs['type']}' (Chrome refuses module "
                                  "scripts from file://)")

        if len(page.toggles) != 1:
            rep.fail("theme", f"{name} has {len(page.toggles)} .theme-toggle "
                              "(must be exactly 1)")
        else:
            tag, attrs, in_header = page.toggles[0]
            if tag != "button":
                rep.fail("theme", f"{name} .theme-toggle is a <{tag}>, not a <button>")
            if not in_header:
                rep.fail("theme", f"{name} .theme-toggle is outside header.site")
            for key, want in TOGGLE_ATTRS.items():
                if attrs.get(key) != want:
                    rep.fail("theme", f"{name} .theme-toggle needs {key}=\"{want}\"")
            for key in TOGGLE_REQUIRED:
                if key not in attrs:
                    rep.fail("theme", f"{name} .theme-toggle is missing '{key}'")

        if len(rep.failures) == before:
            rep.tally("theme")

    css = ROOT / "assets" / "style.css"
    if not css.is_file():
        return
    text = css.read_text(encoding="utf-8")
    blocks = {}
    for label, pattern in DARK_BLOCKS.items():
        m = pattern.search(text)
        if m:
            blocks[label] = css_declarations(m.group(1))
        else:
            rep.fail("theme", f"assets/style.css has no {label} token block")
    if len(blocks) == 2:
        (la, a), (lb, b) = blocks.items()
        drift = sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))
        if drift:
            rep.fail("theme", "assets/style.css dark token blocks disagree on "
                              + ", ".join(drift) + f" ({la} vs {lb})")
        else:
            rep.tally("theme")


def check_meta(rep: Report) -> None:
    """meta.json valid, complete, and internally consistent."""
    for meta_path in sorted(ROOT.rglob("meta.json")):
        if ".git" in meta_path.parts:
            continue
        name = rel(meta_path)
        try:
            data = json.loads(meta_path.read_text())
        except json.JSONDecodeError as exc:
            rep.fail("meta", f"{name} is not valid JSON: {exc}")
            continue

        missing = [k for k in META_REQUIRED if k not in data]
        if missing:
            rep.fail("meta", f"{name} missing key(s): {', '.join(missing)}")
            continue

        kinds = data.get("kinds", {})
        if isinstance(kinds, dict) and sum(kinds.values()) != data.get("parts"):
            rep.fail("meta", f"{name} kinds sum to {sum(kinds.values())} "
                             f"but parts is {data['parts']}")
        elif not isinstance(kinds, dict):
            rep.fail("meta", f"{name} 'kinds' must be an object")
        else:
            rep.tally("meta")

        for k in kinds:
            if k not in KIND_REQUIREMENTS:
                rep.fail("meta", f"{name} has unknown kind '{k}'")

        for field in ("published", "updated"):
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(data.get(field, ""))):
                rep.fail("meta", f"{name} {field} is not YYYY-MM-DD")

        # A book folder must have real parts, not just a meta file.
        if meta_path.parent.name != "_template":
            n = len(list(meta_path.parent.glob("[0-9][0-9]-*.html")))
            if n and n != data.get("parts"):
                rep.fail("meta", f"{name} says {data['parts']} parts "
                                 f"but {n} part file(s) exist")


CHECKS = ["nojekyll", "links", "network", "structure", "a11y",
          "footnotes", "parts", "kinds", "theme", "meta"]


def main() -> int:
    ap = argparse.ArgumentParser(description="Structural checker for The Understudy.")
    ap.add_argument("-v", "--verbose", action="store_true", help="per-file detail")
    ap.add_argument("-q", "--quiet", action="store_true", help="failures only")
    ap.add_argument("--only", choices=CHECKS, help="run a single check")
    args = ap.parse_args()

    level = logging.DEBUG if args.verbose else logging.ERROR if args.quiet else logging.WARNING
    logging.basicConfig(level=level, format="  %(levelname)-7s %(message)s")

    files = html_files()
    if not files:
        print("no HTML files found", file=sys.stderr)
        return 1

    raw: dict[Path, str] = {}
    pages: dict[Path, Page] = {}
    for f in files:
        text = f.read_text(encoding="utf-8")
        raw[f] = text
        p = Page()
        p.feed(text)
        pages[f] = p
        LOG.debug("parsed %s (%d headings, %d links)", rel(f), len(p.headings), len(p.links))

    rep = Report()
    run = (lambda n: args.only in (None, n))

    if run("nojekyll"):  check_nojekyll(rep)
    if run("links"):     check_links(rep, pages)
    if run("network"):   check_network(rep, pages)
    if run("structure"): check_structure(rep, pages)
    if run("a11y"):      check_a11y(rep, pages)
    if run("footnotes"): check_footnotes(rep, pages)
    if run("parts") or run("kinds"): check_parts(rep, pages, raw)
    if run("theme"):     check_theme(rep, pages)
    if run("meta"):      check_meta(rep)

    print(f"\n  {len(files)} pages checked\n")
    failed = {c for c, _ in rep.failures}
    warned = {c for c, _ in rep.warnings}
    for c in CHECKS:
        if args.only and args.only != c:
            continue
        n = rep.counts.get(c, 0)
        mark = "FAIL" if c in failed else "warn" if c in warned else "ok"
        detail = f"{n} passed" if n else "-"
        print(f"  {c:<10} {mark:>4}  {detail}")

    print()
    if rep.failures:
        print(f"  {len(rep.failures)} failure(s), {len(rep.warnings)} warning(s)\n")
        return 1
    print(f"  0 failures, {len(rep.warnings)} warning(s)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
