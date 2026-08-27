# Prompt log

Running log of the prompts that shaped this repository.

> **Note on this file.** §3 of the brief lists `PROMPT.md` as the brief
> itself. The brief is checked in as **[CLAUDE.md](CLAUDE.md)**, which is the
> authoritative copy — duplicating it here would only create drift, so this
> file is the prompt log instead. See README for the two deviations from the
> brief's stated layout and the reasoning behind each.

---

## 2026-08-25 — Task A: bootstrap

**Prompt:** "Bootstrap the project based on the project's claude file."

Executed Task A (§13 of the brief): full tree with `.nojekyll`, the complete
stylesheet, three part templates plus the book-index template and
`meta.json`, `index.html`, `about.html`, `README.md`. No book content.

Four decisions were confirmed before any code was written:

| Fork | Decision | Why |
|---|---|---|
| Aesthetic direction | **Two surfaces** — depth encodes voice | §16 requires stating a direction before writing CSS |
| Typography | Self-host 4 variable woff2 (~173KB, OFL) | §3 specifies `assets/fonts/`; §2.3 forbids a CDN |
| Testing | `tools/check.py`, stdlib only | Reconciles "always set up tests" with "no build step" — a checker never runs at serve time |
| `PROMPT.md` | Prompt log, not a copy of the brief | `CLAUDE.md` is already the checked-in brief |

Deliverable summary in [memory/2026-08-25.md](memory/2026-08-25.md).

## 2026-08-27

- Add book - Surfing Uncertainty.
- (Clarification) The previous sessions shown for this project actually belong
  to the book-reviews project, which was earlier named 'books'. Make a
  permanent distinction so future sessions are not confused, including in any
  folder-scoped memory.
- Implement the plan.
