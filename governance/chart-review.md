# Chart review — Cascadia Control Tower

**2026-08-09.** Against `VIZ-PRINCIPLES.md` v2.2.

> **STATUS: NOT CLEARED TO SHIP.** Rule 7.4's reading panel has not been run.
> This document records the author's own review only — Rule 7.1's author half
> and the Rule 7.3 scored checklist. See §5 for what is outstanding and why it
> cannot be run from the build session.

---

## 1 · Layer 0 declarations

**0.1 — the decision.** Whether to certify one fill definition, and where to set
the split-cost threshold for each banner.

| Question | Answer |
|---|---|
| Whose decision | A fulfilment leader, with a finance partner in the room |
| Horizon | Tactical to strategic — a metric definition and an allocation policy |
| Literacy | High. Both readers are analytics-literate operators |
| Benchmark | Peer XBRL and a federal inventory series for plausibility; an internal counterfactual for the service trade |
| Refresh | None. Frozen snapshot, and the page says so |
| Action | Certify order fill; set two thresholds instead of one; put split rate on the same register as fill rate |

**0.2 — quadrant.** **Explanatory.** The findings are known and the page is
built to make them land. The full explanatory checklist applies to every chart.

**0.3 — chart class.** Seven **detailed** charts. The eight stat tiles in the
overview are signature class and are exempt from C4, C8, C9 and E3.

---

## 2 · Rule 7.3 scored checklist

`(rule, class, weight, evidence)` for every violation that survives.

| Rule | Class | Weight | Evidence | Status |
|---|---|---|---|---|
| 3.2 | INVARIANT | — | Chart 4's annotation says "near-identical **dollar cost**" over a plot whose only axis is percent of margin. The dollar figure is in the title and the data table, not on the marks. | **Accepted.** Rule 3.4 assigns the mechanism to the annotation and the claim to the title; the computed-aggregate exception applies because the table carries both premiums. Recorded rather than waved through. |
| 2.9 | PREFERENCE | 4 | Bar value labels carry two decimals (`17.07%`, `12.09%`) where the rounding rule asks for three significant figures. | **Accepted, weight 4.** The two-decimal form is what makes the 4.1× and 2.1× ratios in the titles checkable against the marks. Rounding to `17%` and `4%` would break Rule 3.2 to satisfy a weight-4 preference. |

**PREFERENCE total: 4. INVARIANT violations: 0.**

Everything else on the explanatory checklist passes. Verified programmatically
against the live DOM: no legend on any chart (every series directly labelled),
all seven carry a real data table wired through `aria-describedby`, all 138
table headers scoped, sequential heading order, no text below 12px, every text
colour ≥4.5:1, decal as a second non-colour channel on all three categorical
charts, keyboard navigators on the three time series whose finding is a shape,
one provenance strip per chart at exactly four segments, and no horizontal
scroll at 320px.

---

## 3 · Author's own review (Rule 7.1, author half)

**The second arrangement is the author's own work, and it had never been done.**
The browser pane would not composite during the build, so every check up to this
point was programmatic — DOM state, chart options, computed contrast, canvas
dimensions, reflow. All of it passed. **None of it looks at the picture.**

Rendering the seven charts to PNG and reading them surfaced thirteen defects,
five of which were fatal to a claim the page makes. The pre-panel notes written
before the render are at `pre-panel-notes-2026-08-09.md`; the "foreseen" column
below is scored against that file, not against memory.

| # | Chart | Defect | Rule | Foreseen | Disposition |
|---|---|---|---|---|---|
| A1 | 1 | Y-axis started at 82%, so order fill's November lows (77.95%) fell **off the bottom of the plot and vanished** — the deepest service failures in the dataset, which are the months the module is about | 4.1 | No | **Fixed.** Axis bounds now computed from the series |
| A2 | 2 | Same clipping: the single-node counterfactual dropped below the 88% floor and disappeared twice | 4.1 | No | **Fixed** |
| A3 | 1, 3 | Titles **clipped mid-word** at the right edge — "…arithmetically corre", "…one cause, two sympto". ECharts does not wrap a title, it truncates it | 3.1 | Partly — notes predicted overflow, not truncation | **Fixed.** Title width set from the container and the plot pushed down by the line count |
| A4 | 3 | Annotation drawn **over the tallest bar**, hiding both the bar top and its 17.07% label. The annotation helper paints a paper-coloured outline around its glyphs, which erases what is underneath | 3.4 | Yes | **Fixed.** Axis headroom reserved; annotations live there |
| A5 | 4 | Annotation hid the Off-Main bar's 12.09% label — **one of the two figures the title cites was unreadable on the plot** | 3.2 | Yes | **Fixed** |
| A6 | 6 | Annotation hid Store 104's value label | 3.4 | Yes | **Fixed** |
| A7 | 5 | Y-axis 0–100 driven by a degenerate $4 point where both banners sit at 100%, squashing the entire informative range into the bottom fifth | 1.3 | Partly | **Fixed.** $4 dropped from the plot, kept in the table and in `validate.py`; subtitle and provenance flag say why |
| A8 | 5 | Both end labels collided into an unreadable overlap at the right edge, and clipped. **The chart shipped with no legend and no readable series identity at all** | 3.6 | No | **Fixed.** Names placed at the point of widest separation |
| A9 | 5 | Annotation was **factually wrong**: "catches most of one banner and little of the other" over values of 20.4% and 14%. Neither is "most"; 14% is not "little" | 3.2 | No | **Fixed.** Rewritten to a claim the plot supports |
| A10 | all | Accessibility summaries contained **invented ranges**. The fills summary told a screen-reader user that order fill ran 85.6–88.6 when it actually reaches 77.95. A sighted reader had the plot to contradict it; a non-sighted reader had nothing | 5.2 | No — notes explicitly listed descriptions as believed sound | **Fixed.** Every figure computed from the same query that feeds the chart |
| A11 | 6 | Title claimed "stores ship 1.9% of units", a variable the chart does not plot | 3.2 | Yes | **Fixed.** Moved to the subtitle and the table |
| A12 | 3 | The two series had **no names on the plot** — two colours and no way to tell which was which | 3.6 | No | **Fixed.** Each series named at its first bar, on different groups so the names cannot collide |
| A13 | 7 | Annotation relocated into the middle of the reference band, legible but no longer pointing at the December dip it explains | 3.4 | No | **Fixed.** Moved under the dip |

**Foreseen 5 of 13.** The three most serious — clipped data, false accessibility
summaries, and a chart with no series identity — were all unforeseen, and all
three passed every programmatic check that had been run.

### What this says about the checks that passed

A11 and A12 are the instructive pair. The page had `role="img"`, authored
`aria-label`s, wired data tables, scoped headers, computed contrast and verified
reflow — and simultaneously a chart whose two series could not be told apart and
a description that lied about the numbers. **Structural accessibility checks and
a legible chart are different properties, and passing the first says nothing
about the second.**

---

## 4 · Second-arrangement note

Charts 1 and 2 were re-read with the axis floor removed, which is the arrangement
change Rule 7.1 asks for. It changed the reading materially: with the floor at
82% the three fill series looked like three flat, parallel, well-behaved lines
and the module's story was carried entirely by the title. With the floor removed
the November collapse dominates the plot, and the seasonal failure — which the
generator produces and the page never previously showed — becomes the visible
feature. **The corrected chart makes an argument the clipped one could not.**

---

## 5 · Rule 7.4 reading panel — OUTSTANDING

**Not run, and deliberately not run from this session.**

The panel's entire value is blindness. Its seats must not see the brief, the
build notes, the generator assumptions, the source data, or any statement of the
intended finding. This session holds all of them. Seats spawned from here would
have blindness that is *asserted by their author* rather than structural, and
the finished review could not distinguish that from the real thing — which is
precisely the failure mode Rule 7.4 names in its own limits section.

**The panel runs in a separate session with no access to this context.** The
handoff is at
`Portfolio Project/docs/Cascadia_ControlTower_Reading_Panel_Handoff_2026-08-09.md`.

Outstanding for that session:

- roster block, cast from the Layer 0 decision above
- four returns per seat per chart
- disposition table with reviewer words quoted verbatim
- **D, N and R.** N is measurable because `pre-panel-notes-2026-08-09.md` was
  written before the charts were rendered and has not been edited since

The seven chart images the panel reads are frozen at `panel/charts/`, rendered
from the corrected page at 1040px wide, 2× scale.

**Until that panel has run and its findings are dispositioned, this module is
not cleared to ship.** A clean author review is not a substitute — this section
of the review exists because the author already demonstrated, thirteen times in
one afternoon, that he could not see his own charts.
