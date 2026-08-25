## 1. Mission

For each book, produce a set of pages that transmit **what the book actually contains** — its arguments, its machinery, its evidence, its cases, its arc — at enough depth and completeness that reading the pages gives you what reading the book would have given you.

Nothing is asked of the reader except attention. There are no exercises, no drills, no flashcards, no homework, no progress tracking. Where this site shows work being done — a mechanism traced through a concrete input, an argument walked through a case — the reader *watches*. That is exposition, not assignment.

### The five tests

| Test | Passes when | Applies to |
|---|---|---|
| **Caught-out** | You could talk about this book for an hour with someone who read it cover to cover and never be caught out — recall the case they raise, know the number they cite, notice when they misremember. | every part |
| **Particulars** | After any page you can name five specific things from it: a person, a place, a number, a study, an anecdote. | every part |
| **Whiteboard** | You could draw the mechanism from memory and narrate one complete operation through it, without notes. | mechanism |
| **Variation** | Someone changes a parameter — bigger pages, another level of hierarchy, a noisier signal, a write-heavy workload — and you can say what happens and why. | mechanism |
| **Contrast** | Someone removes one of the claim's conditions and you can say what the claim then predicts, and whether the record agrees. | claim |
| **Placement** | Someone names an item the book never covers and you can locate it on the axes that organise the space. | terrain |

The particulars test is the cheapest and catches the most: pages made entirely of concepts have failed, because concepts are what survives compression and particulars are what survives *reading*.

The last three are the ones that separate having read about a thing from understanding it, and no amount of fluent prose gets a reader past them.

### What this is not

- **Not a review.** No verdict on whether the book is worth your time, no thesis of the site's own competing with the book's. Evaluation happens, but as a labelled layer on top of transmission (§9).
- **Not a summary.** A summary tells you what a book is about. This tells you what is *in* it — roughly the difference between a menu and a meal.
- **Not "key takeaways."** Takeaways are the residue left after understanding. Distributing the residue and calling it the thing is the central failure this site exists to avoid.

### The honest limit

Some books, and some chapters, cannot be transmitted this way. Where the prose *is* the payload — where the effect comes from accumulation, from voice, from living inside an argument for three hundred pages — the page says plainly that this one has to be read, and says what specifically doesn't survive the transfer. That admission is not a failure of the page. Concealing it is.

---

## 2. Hard constraints

Non-negotiable; every change preserves them.

1. **Static HTML only.** Hand-authored `.html`. No server, no runtime, no API calls, no database.
2. **No build step.** No npm, no bundler, no SSG, no Sass, no templating. What is committed is what is served; opening any `.html` from disk must work.
3. **No external runtime dependencies.** No CDN, no Google Fonts, no analytics, no third-party JS. Everything self-hosted under `assets/`. The site renders fully with the network off.
4. **JavaScript optional and additive.** Every page complete with JS disabled; JS may only enhance, and must never `fetch()` (that breaks `file://`).
5. **Relative links only.** No paths starting with `/`. The tree must work at `https://user.github.io/repo/`, at a domain root, and from the local filesystem, unchanged.
6. **`.nojekyll`** — empty file at repo root.
7. **One folder per book**, linked from the root index.
8. **Accessibility and responsiveness are part of done**: semantic landmarks, one `<h1>` per page, correct heading order, visible keyboard focus, `prefers-reduced-motion` respected, comfortable at 360px, body contrast ≥ 4.5:1. Code and figures must be legible on a phone.

---

## 3. Repository layout

```
/
├── .nojekyll
├── index.html                  ← the shelf
├── about.html                  ← what these pages are, and what they can't do
├── README.md
├── PROMPT.md                   ← this file
├── assets/
│   ├── style.css
│   └── fonts/                  ← self-hosted woff2
├── _template/
│   ├── book-index.html
│   ├── part.html
│   └── meta.json
└── books/
    └── seeing-like-a-state/
        ├── index.html          ← orientation, the arc, the coverage table, how to read this one
        ├── 01-<part-slug>.html ← the readthrough, in parts
        ├── 02-<part-slug>.html
        ├── …
        ├── afterword.html      ← the meta-evaluation, gathered
        ├── glossary.html       ← the book's own vocabulary
        ├── meta.json
        └── figures/            ← hand-authored SVG only
```

Slugs are lowercase-hyphenated and never change once published.

---

## 4. Three kinds of material

**Classify each part, not each book.** Genre is the wrong unit: OSTEP's three-pillar framing is a claim, its locks chapter is a mechanism, and its concurrency-bug taxonomy is terrain. *Seeing Like a State* is mostly claim but its forestry chapter contains a mechanism and its closing chapters are partly terrain. A part declares its kind in `data-kind`, and the kind determines what `read` must contain.

The three kinds get **equal apparatus**. Each has a decomposition, a concrete run, an accounting, and a perturbation test:

| | Claim | Mechanism | Terrain |
|---|---|---|---|
| Decomposition | the joint map | the ratchet | the axes |
| Concrete run | the case walked | the trace | items placed |
| Accounting | the support ledger | the cost sheet | the trade-off across axes |
| Perturbation test | contrast | variation | placement |

### Claim — *the book is arguing that something is true*

Scott's four conditions. Clark's thesis that perception is inference. Simon's argument that professional schools abandoned design.

**Required:** the joint map, the case walked, the support ledger (§7), and the book's cases rendered in enough detail to be remembered rather than merely listed.

### Mechanism — *the book is explaining how something works*

Paging. LSM-trees. Precision-weighting. Two-phase commit. Journalling. Near-decomposability.

**Required:** the ratchet, the trace, the cost sheet, and a figure (§7).

### Terrain — *the book is laying out a landscape*

RAID levels. Isolation levels. Clark's survey of clinical applications. Simon's tour of the design curriculum. Replication topologies.

**Required:** the axes that organise the space, stated before any item is described, then each item placed on those axes. **The failure mode for terrain is the list.** RAID 0/1/4/5/6 enumerated is useless; RAID organised by capacity cost, failure tolerance, and small-write penalty, with each level located on all three, is understanding.

Most parts are mixed. Declare the dominant kind and satisfy the requirements of any kind genuinely present.

---

## 5. Completeness

**Every chapter of the book is accounted for.** Not equally — but every chapter appears in the coverage table on the book's index page with one of four dispositions, and a stated reason for anything short of the first:

| Disposition | Means |
|---|---|
| `full` | Rendered at length, with its cases, machinery, and evidence intact. |
| `condensed` | Covered, but tighter — because the chapter is repetitive or largely restatement. Say which. |
| `folded` | Its content lives inside another part, because splitting it hurt comprehension. Say where. |
| `read-it` | Not transmissible. Say what's in it and why the page can't carry it. |

Silently dropping a chapter is the one unrecoverable failure, because it converts "I read the book" into "I read most of it and don't know which part I'm missing."

**Every load-bearing particular survives.** If the book names a person, place, year, study, quantity, or case that is doing work, it appears. The rule is blunt because the failure is so common: *the moment you write "the author gives several examples," you have deleted the book.*

**Density is not coverage.** A part that mentions eleven case studies in a list has covered none of them. If the book spends nine pages on Brasília, the page spends real space on Brasília.

---

## 6. The shape of a readthrough

### The book index

- **Orientation.** What kind of book this is, what it's trying to do, what world it came out of, what you need before starting.
- **The arc.** How the exposition actually moves, start to finish, in a few paragraphs. The map you hold while reading the parts.
- **How to read this one.** Whether the parts follow the book's order or a better one — and if reordered, the mapping and the reason. Reordering is allowed and sometimes correct; doing it silently is not.
- **The coverage table** (§5).
- **The parts**, each with its kind, length, and what it covers.
- **Whether the book itself is still required**, and for what.

### The parts

A part covers a coherent movement of the book — usually a chapter or a pair, never a fragment of an argument, because the point is to carry the reader through a line of thought rather than hand them pieces of one.

| `id` | What goes here |
|---|---|
| `where` | Two or three sentences of continuity: what's established, what this part does. Written so someone returning after a week can re-enter. For parts with hard dependencies, name them: *assumes parts 3 and 5.* |
| `read` | **The readthrough.** 85% or more of the page. Content requirements set by kind (§4, §7). |
| `voice` | Short. How the book itself handles this material — framing, register, recurring metaphors, characteristic moves. Knowing how a book *feels* is part of having read it. Omit where there's nothing distinctive. |
| `ledger` | What this part **establishes** versus what it **asserts**. Where the prose is more confident than the evidence, or the reverse. Mechanism parts: what the book states without justifying, and what the justification actually is. Claim parts: how the cases were selected. |
| `notes` | The evaluation layer, boxed and labelled (§9). |
| `carry` | What the rest of the book assumes you now have — a recap for the returning reader and the specific hooks the next part will hang things on. |

### The afterword

Gathered meta-evaluation, kept out of the reading so it can't contaminate it: how the book landed and how its reception moved; the strongest critiques from people who understood it, never strawmen; what has held up, what hasn't, what's been superseded and by what; what the book is genuinely for; what its reputation implies it covers but doesn't; where to go next and why.

---

## 7. Writing the readthrough

### General

**Write from understanding, never from the page.** Build the model, close the book, write. Sentence-by-sentence work against the source produces paraphrase, which is both worse reading and a legal problem (§10). Retelling reorganises, connects, and explains what the author assumed you'd infer.

**Explain what the author assumed.** Where the book says "as Polanyi showed" and moves on, spend a paragraph on what Polanyi showed. This is where a readthrough genuinely beats the book, and why a page can be shorter than the chapter and still transmit more.

**Continuous prose.** Bullets only for genuinely enumerable things. A page that is mostly bullets is a summary in costume.

**Never let the site's voice blur into the book's.** The reader must always know whether a sentence is the book's claim or the site's assessment. Attribute inline; anything longer than a clause goes to `notes`.

---

### For claim parts

#### The joint map

Decompose the claim into the conditions it rests on. Number them, because the rest of the part will refer to them by number. State explicitly whether they are **conjunctive** (all required) or **disjunctive** (any suffices) — books almost never say which they mean, and this is where the interesting failure lives.

Then identify which joint is **load-bearing**: the one whose removal changes the outcome most. Naming it is often the single most valuable sentence in the part, because it is what separates the book's catastrophes from the ordinary background functioning of the same forces.

#### The case walked

The trace analogue, and the densest transmission on a claim page. Take one of the book's own cases and run it through the joints **in order**, showing which are present, in what degree, and how the outcome followed. Every step shown, nothing skipped as obvious.

A case narrated as a story is not a case walked. The difference is whether the reader can see the argument's machinery engaging with the particulars.

#### The support ledger

The cost-sheet analogue. Per joint: what evidence is actually offered, of what type — case study, statistics, contemporary testimony, inference from theory — and how much weight it can bear. Then two things claim books systematically leave implicit:

- **How the cases were selected.** A book that examines only failures has selected on the dependent variable, and the reader should know that before deciding what the cases prove. Saying so is not an attack; it's a specification of what the evidence can and can't establish.
- **What the claim buys and pays.** Explanatory reach is purchased with something — usually elasticity. A frame that can be fitted to any outcome after the fact explains a great deal and predicts nothing.

---

### For mechanism parts

#### The ratchet

Technical exposition works by escalation, and so does good conceptual exposition. Transmit the escalation, not the endpoint. Each turn has four moves:

1. **What we have.** The current design, stated so it sounds reasonable — because it was.
2. **What breaks.** The specific case that defeats it, with numbers or a concrete scenario. Not "this is inefficient" — *how* inefficient, on what input.
3. **The fix.** What changes, and why that particular change and not another.
4. **What it costs.** Every fix buys something with something. Name the currency.

Do not skip to the final design. A reader handed multi-level page tables without first feeling the 4MB problem has learned a fact; a reader walked up the ratchet has learned why anyone would build such a thing, which is what lets them reason about the next system they meet. Books that don't ratchet explicitly still have one buried in them — find it and surface it.

#### The trace

At least one complete run of the mechanism on a concrete input, every step shown, real values throughout. A 32-bit address with 4KB pages, walked. A 100-byte record inserted, followed to disk. A specific percept, resolved. No step skipped as obvious; the skipped step is always the one the reader needed.

Keep it proportionate. A trace should show the mechanism's *characteristic* operation, not exhaust its state space — for a protocol with many message orderings, trace the common path in full and then name the interesting divergences rather than running each one.

#### The cost sheet

Brief and structured: what this costs, in what currency (memory, latency, I/O, bandwidth, complexity, generality, falsifiability), and when the cost is worth paying. Two or three sentences or a small table. A mechanism without its cost model is a description, and a reader who has only the description cannot choose.

#### Figures and code

**Figures are content, not decoration.** A mechanism part needs at least one, hand-authored as inline SVG. Label them fully; a figure that requires the prose to be intelligible has failed.

**Code, where the book uses it,** appears as a minimal reimplementation — the smallest version that shows the behaviour — annotated where the interesting line is. Never a transcribed listing (§10). Twenty readable lines beat eighty faithful ones.

---

### For terrain parts

State the **axes first**, before any item is described, and justify them — they are your organising claim about the space, not the book's table of contents. Then place each item on every axis. Close with what the axes reveal that the book's own ordering obscures.

---

## 8. Calibration

The ✗ line is what gets written by default. The ✓ line is the standard.

### Claim

> ✗ Scott's central argument is that state simplification combined with high-modernist ideology has produced catastrophic failures, as in Tanzania's *ujamaa* villagisation programme.

> ✓ Run Tanzania through the joints. **Joint 1** — a state cannot administer what it cannot measure: the rural population was dispersed across scattered homesteads sited by soil and water rather than by any plan, with no address, no register, and no way for Dar es Salaam to deliver a school or count a harvest. **Joint 2** — measurement requires simplification, which discards local particularity: the answer was to gather people into planned villages on a grid, which made them countable, taxable, and serviceable, and which threw away the reason the scattering existed, since the dispersed pattern tracked microvariation in soil, water, and grazing that no survey had captured. **Joint 3** — ideology converts the administrative necessity into a good: Nyerere's programme was never framed as a regrettable compromise but as modernisation itself, the planned village being *better* — aesthetically, morally, developmentally — than the disorder it replaced. **Joint 4** — an authoritarian state and a prostrate civil society remove the correcting feedback: persuasion gave way to compulsion, and no institution remained that could report back that the new sites were failing while there was still time to stop. The outcome is the one the joints predict: millions moved, yields down, a food exporter becoming a food importer.
>
> Now the contrast that shows which joint is load-bearing. Dutch cadastral mapping ran joints 1 through 3 in full — the same measuring impulse, the same discarding of customary particularity, the same conviction that the legible arrangement was the superior one — and stopped at joint 4, because Dutch landholders had courts, property claims, and a press. Outcome: land registration, not famine. **The joints are conjunctive and joint 4 is carrying the argument**, which is what separates Scott's catastrophes from the ordinary functioning of every modern state — including the ones that vaccinate and register land and do it well.

Note what the ✓ version does: the joints numbered and run *in order*, the particulars kept at full resolution inside each joint, the outcome shown following from the structure rather than asserted alongside it, and the contrast case doing the work of identifying what actually matters.

### Mechanism — technical

> ✗ Paging divides memory into fixed-size pages, with a page table mapping virtual pages to physical frames. Because a single-level page table would be too large, most systems use multi-level page tables.

> ✓ Start with the obvious design: one flat array of page-table entries, indexed by virtual page number. A 32-bit address space with 4KB pages has 2²⁰ pages, and at 4 bytes per entry that is **4MB of page table — per process**. Ten processes and you have spent 40MB of physical memory on bookkeeping before running any code. Worse, nearly all of it is wasted: a typical process uses a sliver near the bottom for code and heap, a sliver at the top for stack, and nothing at all in the vast middle, so most of those four million bytes describe pages that do not exist. The fix is to page the page table itself. Split the index: the top ten bits select an entry in a *page directory*, which points at a page-sized chunk of a thousand entries, and the next ten bits select within that chunk. Now a process using only code, heap, and stack allocates the directory (4KB) plus three inner pages (12KB) — **16KB instead of 4MB**, and the unused middle costs nothing but invalid directory entries. What it costs: translation now takes two memory accesses before the access you actually wanted, so every load has silently become three. Which is why the next thing any real system needs is a cache for translations, and why the TLB chapter follows this one.

### Mechanism — conceptual

> ✗ Clark argues that the brain weights prediction errors by their precision, which explains phenomena like attention.

> ✓ The basic story so far: predictions descend, errors ascend, the model updates. But run it in fog. Your visual signal is unreliable — mostly noise around a weak shape — and if that error ascended at full strength you would revise your model of the world on the strength of noise, and hallucinate shapes into the mist. So error cannot be taken at face value; it has to be scaled by how much the system expects that channel to be worth listening to. That scaling term is **precision**, formally the inverse variance of the expected noise. Now notice what a precision knob does: turn it up on one channel and that channel dominates the update, turn it down and it is nearly ignored. That is a description of attention — and the claim is not that precision *explains* attention but that they are **the same operation**, seen from two directions. The same knob at pathological settings gives the book its clinical chapters. What it costs: precision is estimated by the system from its own model, which means the model decides how far to trust the evidence against it. That is elegant, and it is precisely the mechanism critics point to when they argue the framework can absorb any result.

### Terrain

> ✗ RAID comes in several levels. RAID 0 stripes for performance, RAID 1 mirrors for redundancy, RAID 4 uses a dedicated parity disk, RAID 5 distributes parity, and RAID 6 tolerates two failures.

> ✓ Every RAID level is a position on three axes, and once you see the axes the levels stop needing to be memorised: **how much capacity you give up**, **how many simultaneous disk failures you survive**, and **what a small random write costs you**. Striping alone spends no capacity and survives nothing — one disk dies and the array is gone — but a small write costs exactly one write. Mirroring survives any single failure and gives up half the capacity, at two writes per small write. Parity is the attempt to buy failure tolerance without paying half your capacity: one disk's worth of redundancy across the set. It works, and the third axis is where the bill arrives — updating one block means reading the old block and the old parity, computing, and writing both back: **four I/Os for one small write**, the penalty that dominates every real conversation about parity RAID. Putting parity on a dedicated disk makes that disk the bottleneck, since every write touches it; distributing parity is the same scheme with the bottleneck spread out. Surviving two failures needs two independent parity computations — another disk's capacity and a worse write path again.

---

## 9. The evaluation layer

Meta-evaluating means saying how well the book does what it does — but it must never leak into the transmission, or the reader stops being able to tell the book from the page.

- Evaluation lives in `notes` blocks and the afterword. Nowhere else. Inside `read`, the site is transmitting; disagreement is limited to attribution ("the book treats this as settled; it isn't — see notes").
- `notes` blocks are **visually unmistakable**: a marked aside, obviously the site speaking.
- Evaluation is specific. "Some critics have questioned this" is worthless. Who, on what grounds, and what did the book's defenders say back?
- Cover, where relevant: replication status of cited studies; whether a described system still works that way, or whether the hardware assumptions still hold; contested history; what the field concluded afterward; the strongest objection the book doesn't answer.
- **Fairness is a requirement, not a courtesy.** For contested material, present the dispute rather than adjudicating it, and give the book's side its best form.

---

## 10. Accuracy and copyright

- **Never invent.** No fabricated quotes, page numbers, statistics, dates, benchmark figures, study results, or attributions. If a particular can't be verified, research it or leave it out. A confidently wrong detail is worse than a missing one, because the reader will repeat it.
- **Research before writing.** Confirm what the book says, which edition, and the current standing of its claims. Where a book cites a study, check whether it held up; that goes in `notes`.
- **Verify the machinery too.** Traces must actually work and their arithmetic must be checked. Case walks must reflect what actually happened, with dates and magnitudes confirmed against sources outside the book. A wrong intermediate value teaches a wrong mechanism, convincingly.
- **Distinguish three voices:** the book's claim, established consensus, and the site's inference. Never let the third borrow the authority of the first two.

**On copyright:** transmitting a book's *ideas, facts, and arguments* in your own words is legitimate and is what every good lecture course does. Reproducing its *expression* is not.

- **Write from your model, never alongside the text.** If your paragraphs map onto the author's paragraphs, you have paraphrased rather than retold.
- **Quotes short (under ~15 words), exact, attributed, rare.** Never poetry, never lyrics.
- **Reorganise.** A retelling that follows the book's headings beat for beat is closer to a condensation than an explanation.
- **Code is reimplemented, never transcribed.** Diagrams likewise — hand-authored SVG, never traced from the book's figures.
- **Point at the book.** Every book index links to where it can be bought or borrowed — and where a book is distributed free by its authors, as OSTEP is, link there and say so.

---

## 11. Length

**Every number here is a floor. None is a target and none is a ceiling.**

- A part covering a substantial chapter: **~2,500 words.**
- A full book readthrough: **~15,000 words**, considerably more for long or dense books. OSTEP and DDIA will run well past 30,000.

Length is a symptom, not the goal; the gates are the coverage table and the five tests. Two failure modes, the first far more common:

- **Compression by default.** Cutting a case, a ratchet turn, a case walk, or a trace because the page is getting long. The page is *supposed* to get long — that is what "without having read the book" costs. Anything cut takes a `condensed` disposition and a stated reason, never a silent deletion.
- **Padding.** Restating a point three ways, or narrating your own process. If you're inflating, you don't have the material yet.

---

## 12. Page and site specification

### Part pages

A claim part; a mechanism part swaps `.joints`/`.case-walk`/`.support` for `.ratchet`/`.trace`/`.costs` plus a figure.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Part 6 · Villagisation — Seeing Like a State</title>
  <link rel="stylesheet" href="../../assets/style.css">
</head>
<body>
  <a class="skip" href="#main">Skip to content</a>
  <header class="site">
    <a href="../../index.html">The Understudy</a> /
    <a href="index.html">Seeing Like a State</a>
  </header>

  <main id="main">
    <article class="part" data-kind="claim">
      <p class="eyebrow">Part 6 of 9 · claim · covers chapter 7 · ~26 min</p>
      <h1>Villagisation, and the joint that does the work</h1>

      <section id="where">…</section>

      <section id="read">
        <ol class="joints">
          <li id="j1">…</li><li id="j2">…</li><li id="j3">…</li><li id="j4">…</li>
        </ol>

        <div class="case-walk">
          <h3>Tanzania, joint by joint</h3>…
        </div>

        <div class="case-walk contrast">
          <h3>The contrast: the Netherlands</h3>…
        </div>

        <aside class="note">
          <p class="note-label">Note</p>
          <p>…</p>
        </aside>

        <table class="support">…</table>
      </section>

      <section id="voice">…</section>
      <section id="ledger">…</section>
      <section id="notes">…</section>
      <section id="carry">…</section>
    </article>

    <nav class="pager" aria-label="Parts">
      <a rel="prev" href="…">←</a><a rel="next" href="…">→</a>
    </nav>
  </main>
  <footer class="site">…</footer>
</body>
</html>
```

Requirements: `id` on every heading; a table of contents on parts over ~4,000 words; prev/next between parts; `aside.note` styled so it can never be mistaken for body text; footnotes as `<sup><a>` pairs with return links, no JS; `.joints`, `.case-walk`, `.support`, `.ratchet`, `.trace`, `.costs` each with a distinct, consistent treatment so they're findable while scrolling; figures as inline `<svg>` in `<figure>` with `<figcaption>`; code in `<pre><code>` with a language class, readable at 360px, highlighting hand-applied or absent.

### `meta.json`

```json
{
  "slug": "seeing-like-a-state",
  "title": "Seeing Like a State",
  "author": "James C. Scott",
  "year": 1998,
  "domains": ["Political economy", "Development", "Systems"],
  "parts": 9,
  "kinds": { "claim": 6, "mechanism": 1, "terrain": 2 },
  "words": 23800,
  "reading_minutes": 108,
  "chapters_covered": { "full": 8, "condensed": 2, "folded": 0, "read_it": 1 },
  "book_still_required": "For chapter 9 on mētis — the argument there is cumulative and doesn't survive retelling.",
  "prerequisites": [],
  "status": "complete",
  "published": "2026-08-18",
  "updated": "2026-08-18"
}
```

### Site chrome

**`index.html`** — the shelf, regenerated by the agent from the `meta.json` files, never client-side. Each book shows author, year, part count and kind mix, total words, reading time, coverage summary, prerequisites, and whether the book is still required. Grouped by domain.

**`about.html`** — what these pages are, the five tests, and an honest statement of what a readthrough cannot do.

**`assets/style.css`** — one file: reset → tokens → typography → layout → components → print. Light and dark via `prefers-color-scheme`. Print stylesheet producing a genuinely readable long document with figures intact.

### Design

These pages are read for an hour at a time, so typography is the product: measure 62–72 characters, line-height ~1.65, ≥18px desktop and ≥17px mobile, generous space between sections. Code needs a real monospace face and room to breathe.

Two things carry more weight than the rest. **`aside.note`** is the visible boundary between the book and the site's opinion of it — unmistakable at a glance, without shouting. **The concrete-run blocks** (`.case-walk`, `.trace`) are where understanding actually transfers, and a reader scanning back through a part is almost always hunting for one. Give the two of them a shared visual family, since they play the same role in different material.

**Avoid the defaults this brief attracts:** cream `#F4F1EA` + high-contrast serif + terracotta `#D97757`; near-black with one acid accent; faux-broadsheet hairline rules. Choose a direction justifiable in one sentence tied to what these pages do, state it before writing CSS, and record it in `about.html`.

---

## 13. Workflow

### Task A — Bootstrap (once)

1. Build the tree in §3 including `.nojekyll`.
2. Write `assets/style.css` in full. Test against dummy parts of all three kinds, containing all six sections, `.joints` / `.case-walk` / `.support`, `.ratchet` / `.trace` / `.costs`, several `aside.note` blocks, a long stretch of unbroken prose, a code block, footnotes, and an SVG figure.
3. Write `_template/book-index.html` (with the coverage table), `_template/part.html` (all three kind variants, annotated), `_template/meta.json`.
4. Write `index.html` (framing copy, empty but complete shelf), `about.html`, `README.md`.
5. Verify: `file://`, every relative link, dark mode, 360px, keyboard focus, offline, print.
6. **Write no book content in this task.**

### Task B — Read a book

1. **Establish the book.** Actual contents, chapter structure, edition, and the current standing of its claims. Use available tools. Do not write from vague recall — that is how invented particulars get in.
2. **Build the coverage plan.** Chapter list, dispositions, part boundaries, the kind of each part, and whether the order changes. **Show this before writing any parts.**
3. **Write the book index**: orientation, arc, how to read this one, coverage table.
4. **Write the parts**, in order, each complete before the next, so continuity is real rather than retrofitted. Build the kind's decomposition and concrete run *first* — joint map and case walk, or ratchet and trace. They are the spine, and prose written before them tends to describe conclusions.
5. **Verification pass.** Every factual particular confirmed. Every trace re-executed and its arithmetic checked; every case walk checked against sources outside the book.
6. **Particulars pass.** Names, dates, numbers, studies, cases present. Every "several examples" is a defect.
7. **Separation pass.** Every sentence unambiguously the book's or the site's; stray assessment moved into `notes`.
8. **Perturbation pass.** For each part, run its kind's test three times — three variations for a mechanism, three joint-removals for a claim, three unlisted items for terrain — and check the page answers them. Any it doesn't is a hole in the exposition; fix the page, don't add an exercise.
9. **Write the afterword and glossary.**
10. **Build the pages**, fill `meta.json`, draw figures, regenerate `index.html`, cross-link related books both ways.
11. **Verify** (§14).
12. Report: the coverage table, anything below `full` and why, unverified particulars, and where transmission is weakest.

### Task C — Revise one part

Task B steps 4–11 scoped to one part. If boundaries move, update the coverage table and the neighbouring `where` and `carry` sections so continuity survives.

---

## 14. Definition of done

- [ ] Every chapter in the coverage table with a disposition; anything below `full` has a stated reason.
- [ ] Caught-out and particulars tests pass on every part.
- [ ] Each part declares its kind and satisfies that kind's requirements.
- [ ] **Claim parts:** joint map with conjunctive/disjunctive stated and the load-bearing joint named; at least one case walked joint by joint; a contrast case; support ledger including how cases were selected. Contrast test passes.
- [ ] **Mechanism parts:** ratchet, trace with real values, cost sheet, figure. Whiteboard and variation tests pass.
- [ ] **Terrain parts:** axes stated and justified before any item; every item placed on every axis. Placement test passes.
- [ ] Every trace re-executed and every case walk externally checked.
- [ ] No sentence of the form "the author discusses several examples."
- [ ] All six sections present, none empty.
- [ ] Prose-first; bullets only for genuinely enumerable content.
- [ ] Book's voice and site's distinguishable in every sentence; assessment confined to `notes` and afterword.
- [ ] Nothing invented; particulars verified; quotes short, exact, attributed, rare.
- [ ] Code reimplemented not transcribed; figures hand-authored; no paragraph-level tracking of the source.
- [ ] Whether the book is still required stated honestly on the index.
- [ ] `meta.json` accurate; `index.html` regenerated; cross-links both ways.
- [ ] Valid HTML, one `<h1>`, correct heading order, working pager and footnote round-trips.
- [ ] All links relative; nothing loads from the network.
- [ ] Renders at 360px, dark mode, JS disabled, offline, `file://`, and print.
- [ ] `.nojekyll` still at root.

---

## 15. Seed library

Kind mix and the particulars that must survive — a floor on specificity, not a table of contents.

### Seeing Like a State — James C. Scott (1998) · *mostly claim*

The four joints, established early and referred to by number throughout. **Mechanism:** scientific forestry as an actual mechanism — the *Normalbaum*, the reduction of a forest to board-feet, the yield tables, and the second-rotation collapse, which is a ratchet whether or not Scott presents it as one. **Claims walked:** cadastral mapping against customary tenure; permanent surnames and where they came from; standard measurement displacing local units and why local units weren't stupid; Le Corbusier, the Plan Voisin, the Ville Radieuse; Brasília — Costa's plan, the *superquadras*, the abolished street corner, *brasilite*, and Núcleo Bandeirante growing up alongside; Soviet collectivisation; Tanzanian *ujamaa* — Nyerere, the campaign, its scale, its outcome. **Contrast cases are mandatory**, since without them the four joints look like a single undifferentiated force: the Netherlands, and any modern state that measures well. Jane Jacobs as counterweight, Chandigarh as comparison, Lenin's vanguard and Luxemburg's reply. **Terrain:** the closing chapters on *mētis* — the Greek framing, apprenticeship, why local knowledge resists codification — organised by what kind of knowledge resists what kind of capture.

### Operating Systems: Three Easy Pieces — Arpaci-Dusseau & Arpaci-Dusseau · *mostly mechanism*

*(The title is "Three Easy Pieces," not "3 Easy Steps." The authors distribute it free online; link there.)* The three-pillar framing as a claim about what an OS *is*; the dialogues and crux boxes as a device worth transmitting. **Virtualisation:** limited direct execution and trap mechanics; context-switch steps; MLFQ with its starvation and gaming problems and the boost that patches them; lottery and stride. Address translation from base-and-bounds through segmentation to paging; free-space management; the page-table ratchet; TLBs and why they're structural; multi-level tables; swapping and replacement with the clock approximation. **Concurrency:** threads and the shared-stack problem; locks from test-and-set through ticket to two-phase; condition variables and why `while` not `if`; semaphores; the empirical bug study on atomicity versus order violations; deadlock's four conditions and which one each remedy attacks. **Persistence:** disk geometry and why seek dominates; RAID as terrain; files, directories, VSFS layout; FFS cylinder groups; journalling and its ordering constraints; LFS and the garbage-collection problem it creates; SSDs and the FTL; NFS statelessness and AFS caching.

### Designing Data-Intensive Applications — Martin Kleppmann (2017) · *mechanism + terrain*

Reliability, scalability, maintainability; the Twitter fan-out example; percentiles as the honest latency metric. Data models as terrain. Storage engines as a ratchet: log, hash index, SSTable, LSM, with B-trees as the other branch and write-amplification arithmetic done properly. Column storage. Encoding and the compatibility problem that motivates it. Replication topologies as terrain; read-your-writes, monotonic reads, quorums, LWW, version vectors. Partitioning, secondary indexes, rebalancing. Transactions: what ACID promises, then isolation levels as terrain organised by anomaly permitted — read committed, snapshot isolation and MVCC, lost updates, write skew, phantoms — then the three routes to serializability. Unreliable clocks and process pauses. Linearizability, causality, total order broadcast, 2PC, consensus, ZooKeeper. MapReduce and dataflow engines; logs versus messaging, CDC, event sourcing, windows, stream joins; unbundling the database, and the ethics chapter.

### Surfing Uncertainty — Andy Clark (2016) · *claim + mechanism*

The thesis that perception is inference, with its joints mapped and its load-bearing one named. The machinery as a ratchet: generative models, error as the ascending signal, hierarchy, precision as gain (§8). Binocular rivalry and the hollow-face illusion. Motor control recast as active inference, collapsing perception and action into one operation. The dark-room problem and Clark's answer. The clinical chapters as terrain — autism, positive symptoms, placebo — organised by which parameter is disturbed. The connection back to extended mind. And what "surfing" is meant to convey about a brain that never lands.

### The Sciences of the Artificial — Herbert A. Simon (1969; 3rd ed. 1996) · *claim + mechanism*

The artefact as interface between inner and outer environment, and what that licenses. The ant on the beach. Bounded rationality and satisficing in Simon's own terms — claims about search under cost, not "people are irrational." The chess and problem-solving material. Hora and Tempus with the actual arithmetic, and near-decomposability as the general result — the most exportable mechanism in the book, and one that deserves a full ratchet and trace. The empty-world hypothesis. Memory, chunks, and the limits of the human processor. The argument that professional schools abandoned design, and the curriculum Simon proposed to put it back.

---

## 16. Your first task

Execute **Task A** (§13): full tree, `.nojekyll`, complete stylesheet, three templates, `index.html`, `about.html`, `README.md`.

Before writing any CSS, state in two or three sentences the aesthetic direction and the one-sentence justification tying it to what these pages do (§12) — paying particular attention to how `aside.note` reads against the body, and how `.case-walk` and `.trace` share a visual family.

Write no book content. When the bootstrap verifies, stop and report what you built, and which book you'd start with and why.