# Learnings

Gotchas specific to this codebase, recorded as they are found. Read before
making changes; add to it when something surprises you.

---

## The `:target` highlight "not working" was test contamination

Injecting a `<style>` element to preview the print rules on screen leaves the
document altered until a **real** reload — and navigating to the same URL with
only a different fragment does *not* reload. The print block sets
`.footnotes li:target { background: none }`, so the footnote highlight
measured as broken while the stylesheet was in fact correct.

**Rule:** tear down injected test styles explicitly, or force a genuine reload
before trusting the next measurement. Verify the page is clean
(`document.getElementById('print-preview')`) before concluding a CSS rule is
broken.

## Measuring layout inside a `document.write` iframe races the stylesheet

A harness that wrote each page into a hidden 360px iframe reported horizontal
overflow on exactly the two pages with wide content (a five-column table, a
long code block). Both were false: the iframe had not loaded `style.css` yet,
so it had no `overflow-x: auto` containers at all, and every wide element
overflowed. The give-away was in the network log — 404s for
`_template/assets/style.css`, a path no real page requests.

**Rule:** measure responsive layout in the real viewport. If you must use an
iframe, assert the stylesheet applied (`getComputedStyle(body).fontFamily`)
before measuring.

## `getBoundingClientRect()` lies about elements inside scrollers

A child inside `overflow-x: auto` still reports its full extent past the
viewport, even though it is visually clipped and scrollable. A naive "which
elements stick out" probe therefore flags exactly the elements you
deliberately made scrollable.

**Rule:** the honest test for sideways scroll is
`documentElement.scrollWidth > clientWidth`, plus filtering to elements whose
*nearest scrollable ancestor* is the document itself.

## `white-space: nowrap` outside a scroller is a 360px bug

`.val` held a 36-character expression and pushed the page body 50px wide at
360px. Values now use `overflow-wrap: break-word` and wrap at spaces; write
short values that must stay together with `&nbsp;`.

**Rule:** anything with `nowrap` must either be short or live inside
`pre` / `.table-wrap` / `.support-wrap` / `.coverage-wrap`.

## Traces must be executed, not proofread

The mechanism template's trace shipped with `(0x0092 << 12)` written out as
`0x0092_0000` — a shift of 16 instead of 12. Every intermediate field was
correct and the prose read fluently; only the final combine was wrong. A
reader would have absorbed the wrong page-shift without hesitating.

**Rule:** run every trace through an interpreter and diff the result against
the page. This is the brief's §10 in practice: "a wrong intermediate value
teaches a wrong mechanism, convincingly."

## A checker that has never failed proves nothing

The first version of the kind check used a substring match, so a page whose
`ol.joints` had been renamed still passed — the word "joints" appears in the
surrounding prose. The fix over-corrected into a regex that anchored `^`
inside a character-consuming context and failed *every* page. Both bugs were
found by a negative test that breaks one thing per check in a scratch copy of
the tree.

**Rule:** after changing `tools/check.py`, re-run the negative test. A green
run against a correct tree cannot tell a working checker from a broken one.

## Background graphics do not print

Browsers omit them by default, so the sunk/raised grounds that carry the whole
design collapse to white on paper. The print block re-encodes the same
distinction as borders — a full box for notes, a heavy left bar for worked
runs.

**Rule:** any new component that carries meaning in its background needs a
print rule that carries the same meaning in ink.

## SVG text scales with the drawing

There is no build step and no second drawing, so a wide `viewBox` produces an
illegible figure on a phone. Figures are authored at ~420 units wide and
capped at `34rem`, keeping labels between ~12px at 360px and ~20px on desktop.

**Rule:** figures use the `.fig-*` classes and never hardcode a fill — a
hardcoded figure is invisible in dark mode.

## `unicode-range` on one face of a family is a trap

It was originally set on the Literata roman but not the italic, which would
have made the two fall back inconsistently for any codepoint outside the
declared range. With a single subset per family it buys nothing at all, so it
was removed.

## `.nojekyll` is not optional

GitHub Pages runs Jekyll by default, and Jekyll skips directories beginning
with an underscore — which would make `_template/` vanish from a deployed
site.

## A folder path is not a project identity

This repo lives at `my docs/books`, a path previously occupied by a *different*
project — `digster/book-reviews`, renamed away on 2026-08-18. The Understudy
was then bootstrapped at `~/lab/books` and copied in on 2026-08-25. Claude Code
keys sessions, transcripts and per-project memory by absolute path alone, with
no repo UUID and no remote check, so two unrelated projects ended up sharing one
history: renaming a folder orphans its past under the old slug, and reusing a
freed path silently inherits that slug's contents. The give-away was a session
titled "Home feed post duplication" — this site has no feed and no posts.

**Rule:** trust the git remote and `README.md`, not the folder name or the
session list, when identifying which project you are in. Anything about a home
feed, post categories or review posts belongs to `book-reviews`. Markers that
must survive a move go in git-tracked files; `~/.claude` memory is keyed by the
very thing that breaks.

## The preview pane does not apply `:target`, and sanitises the CSSOM

A second `:target` false negative, with a different cause than the first. In the
in-app preview pane, `.footnotes li:target` matched via `matches(':target')` and
via `querySelector`, `--accent-tint` resolved to a real colour, and the computed
background was still transparent. The tell was that a *pre-existing* rule —
`ol.joints > li:target::before`, verified working during bootstrap — failed
identically. The pane also reports `selectorText` as undefined on all 260
parsed rules, so any probe that walks `document.styleSheets` looking for a
selector silently finds nothing and reads as evidence of a missing rule.

Two further pane artefacts cost time in the same session: `documentElement.clientWidth`
reads `0` until an explicit `resize_window`, which makes every overflow
measurement report a false positive; and a `file://` page opens as a `data:`
snapshot, so relative `../../assets/style.css` never loads and the page renders
unstyled.

**Rule:** before trusting a negative rendering result in the pane, reproduce it
against a rule known to work. Always `resize_window` to an explicit viewport and
assert `getComputedStyle(body).fontFamily` before measuring, and serve over
`http://` rather than opening `file://` in the pane. `getComputedStyle` on real
elements is reliable; CSSOM introspection and `:target` are not.

## Author `display` silently overrides the `hidden` attribute

`[hidden] { display: none }` is a user-agent rule, and any author rule that
sets `display` beats it whatever its specificity. The theme switch relies on
this on purpose: it carries `hidden` for no-JS readers, and
`:root[data-theme] .theme-toggle { display: inline-flex }` shows it from the
first frame. The same fact is a trap everywhere else. Put `display: flex` on a
base class, and every `hidden` element with that class reappears.

**Rule:** never set `display` in a component's base rule if its markup may
carry `hidden`; set it only under the condition that should reveal it.

## Checking a test only after load can miss a first-frame bug

Two theme tests passed against deliberately broken copies. One asserted the
switch was visible, but `theme.js` removes `hidden` on DOMContentLoaded, so
deleting the CSS that shows it from the first frame changed nothing the test
could see. The other checked `body` colours in print, but the print block
hard-codes them, so dark tokens leaking into print were invisible there. The
fixes were a MutationObserver probe that records state when the parser
inserts the switch, and asserting on the tokens themselves.

**Rule:** for a first-frame property, observe it before DOMContentLoaded. For
a token cascade, assert on the token, not on an element that might hard-code
the value. Then break the implementation and watch the test fail.

## A theme override needs `:where()`, or print inherits it

`:root[data-theme="dark"]` weighs (0,2,0) and beats the print block's plain
`:root` (0,1,0) whatever the source order, so printing from dark mode would
pull dark ink tokens onto white paper. Both dark-token selectors are wrapped
in `:where()` to weigh exactly what `:root` does, and print wins by coming
later.

**Rule:** any selector that sets theme tokens must weigh no more than `:root`.

## Module scripts do not run from `file://` in Chrome

`<script type="module">` is fetched with CORS, and `file://` has no origin to
satisfy it, so Chrome refuses it. `file://` is a required surface here. Scripts
are classic, and the checker fails `theme.js` loaded as a module.

## Chromium blockifies a flex item's `inline-flex`

The switch is declared `display: inline-flex` but computes as `flex`, because
it is a child of the flex header. An assertion on the exact value failed
while the page was correct. Assert on what matters (`!= "none"`).
