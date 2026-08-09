# Chart review — Cascadia Control Tower

**2026-08-09.** Against `VIZ-PRINCIPLES.md` v2.2.

> **STATUS: CLEARED TO SHIP.** Rule 7.4's reading panel ran on 2026-08-09 from a
> fresh session (§2). Four blind seats returned 25 findings; 20 were dispositioned
> as defects, 13 fixed, 7 accepted with reasons recorded. `validate.py` passes
> 12/12 against the rebuilt page.
>
> **D = 2.86 · N = 0.80 · R = 0.20.** Carry these forward — the Rule 7.4
> retirement trigger needs three consecutive modules and this is one of them.
> Nothing here fires it: N at 0.80 says the panel found four defects in five
> that the author had not, on charts he had already corrected once.
>
> Two things this clearance does **not** cover, stated so they are not read as
> covered: the shipping render (§6) has not itself been panelled, and four open
> items the panel raised are closed by no fix (§2.6).
>
> **Viewports reviewed: 390 · 414 · 768 · 1440 (§7).** §2–§6 were conducted at
> 1006px only; §7 is the responsive review and supersedes the Layer 5 portion of
> §3. Three charts miss the 65% plot-width floor at 390px for a reason that is
> arithmetic rather than oversight — recorded in §7, not waved through.

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

## 2 · Rule 7.4 reading panel

Run 2026-08-09 from a fresh session holding none of the build context, per the
handoff. Verbatim returns are annexed at `reading-panel-returns-2026-08-09.md`;
the disposition table below quotes them directly.

### 2.1 · Roster

```
READING PANEL — Cascadia Control Tower — 2026-08-09
Decision served (Rule 0.1): a fulfilment leader with a finance partner in the
  room, deciding whether to certify one fill definition and where to set the
  split-cost threshold for each of two banners
Charts panelled: 7   States: default only
Nature: simulated

  Seat 1  Director of Distribution Centre Operations, 16 years, single large
          outbound DC in the Seattle metro
          — why this seat: owns the service number the decision would certify.
            Whether a fill definition is one he can be held to, and whether what
            drags it down is inside his four walls or upstream in inventory
            placement, is the question he brings to the room.
  Seat 2  Director of Supply Chain Finance, 11 years, closes the books
          — why this seat: owns the margin the service costs, and sets the
            threshold. Will not let a business case be built on an allocated
            number, so he tests every cost on the page for whether it is
            incremental cash.
  Seat 3  VP of Merchandise Planning, off-price banner, 19 years, not an analyst
          — why this seat: the banner the threshold decision lands hardest on.
            Buys and places the inventory whose thinness the page is describing,
            and is the room's least analytics-literate real reader — Rule 0.1
            claims high literacy for the two owners, and a roster of three
            experts would quietly assume that answer for everyone.
  Seat 4  visualization reader   — simulated — canvas only; tables and
            arithmetic excluded

Blindness asserted: design system ☑ · review and build notes ☑ · source data ☑ ·
                    intended finding from outside the artifact ☑ ·
                    other seats' output ☑
Run: parallel ☑    Author's pre-panel notes recorded: ☑
```

All four seats were spawned in a single message, given the seven PNGs at
`panel/charts/` by absolute path, and instructed that those seven files were the
only thing they could open. Per the skill's own limits section: **blindness and
parallelism are self-attestation.** Nothing in this document distinguishes four
parallel blind seats from one sequential run. What is checkable is below — a
stated reason per seat, four items returned per seat per chart, a location for
every quoted number, and a disposition for every finding.

### 2.2 · Returns

Full and unedited at `reading-panel-returns-2026-08-09.md`. Two properties of
the returns are worth recording here because they bear on how much the panel is
worth:

**The sentences were not bland, and they did not simply agree with the title.**
Rule 7.2's caution is that model chart *judgment* measures worst on summary
tasks, which is exactly what "the sentence" is. Two of the seven charts drew a
sentence that actively refused the title's claim — seat 1 on chart 7 opened
*"This one I'd flag as apples to oranges"* and seat 2 *"we're either far leaner
than the sector or we're not measuring the same thing."* A seat that were merely
paraphrasing the headline could not produce that.

**The number field did the job it exists for.** On chart 2 seat 3 wrote *"2.7
points, off the headline. I couldn't get that off the picture"* — an explicit
admission that the figure was unlocatable on the marks. Across the panel, four
headline figures were sourced to the title rather than to any mark.

### 2.3 · Disposition

Sorted by number of seats, descending.

| # | Finding, in the reviewer's words | Seats | n | Chart | Defect? | Novel? | Disposition | Rule |
|---|---|---|---|---|---|---|---|---|
| 1 | *"Five of the seven headline numbers are not on their plots."* — and independently, seat 3 on chart 2: *"I couldn't get that off the picture"* | 1,2,3,4 | **4** | 1,2,4,7 | yes | yes | **accepted** — every one is a computed aggregate over 24 months (a mean gap, a mean ratio, an order-weighted mean premium). No single mark can carry a mean, and a reference line drawn at one would assert a constancy the data does not have — chart 1's gap runs 5.3 to 11 points. Each figure is in the chart's table and its computed description. Recorded rather than waved through: four of four seats reached for these numbers and none could point at one. | 3.2 |
| 2 | *"the $4 point is dropped off the plot and only mentioned in the note, which stopped me for a second while I worked out why the line starts at $5"* | 1,2,3,4 | **4** | 5 | yes | no | **accepted** — plotting $4 forces a 0–100 axis, because every split clears one extra parcel base rate and both banners sit at exactly 100% there; that squashed the informative range into the bottom fifth and was itself defect A7. Kept in the table, in `validate.py`'s monotonicity check, and named in both the subtitle and the provenance flag. Scored not-novel: the omission and its reason are recorded in the chart's source comment, written before the panel. | 3.2 |
| 3 | *"if $5.46 is a blended network number and Alder & Vance actually ships heavier, more expensive parcels, then this chart is flattering them and I've been handed the bad end of an average"* — seat 2: *"is that $5.46 an average across both banners, or the same charge applied to both?"*; seat 1: *"is it one flat number applied to every split"* | 1,2,3 | **3** | 4 | yes | yes | **fixed** — the seats were right and the title was wrong. $5.46 is the order-weighted blend of $5.64 (Off-Main) and $5.18 (Alder & Vance); "the same $5.46 second parcel" asserted an equality the data does not contain. Title now names both premiums. **All three domain seats independently distrusted this number.** | 3.2 |
| 4 | *"If slow movers are three percent of my lines then 17% of them is a rounding error and I don't want a task force."* — seat 2: *"Three bands with no sense of how big each one is, so I can't turn any of this into money."* | 1,2,3 | **3** | 3,4 | yes | yes | **fixed** — band share of lines now on chart 3's axis (70% / 22% / 8%), and each banner's split share and order count on chart 4's (12% · 26,757; 11% · 17,367). | 5.1 |
| 5 | *"we're looking at a chart whose most expensive bars are two percent of the business — that belongs on the chart, not underneath it"* | 1,2,3 | **3** | 6 | yes | no | **fixed** — each node's unit share now sits under its name on the axis. Scored not-novel: pre-panel note 2 predicted the volume share would be unreadable from the marks. The author's remedy had been to move it to the subtitle; three blind readers said that was not enough. | 5.1 |
| 6 | *"we're a fraction of a company against a whole company and the comparison flatters us badly"* — seat 1: *"that isn't a win, it's a different measurement"*; seat 3: *"I don't want to walk into a room and say we're four times leaner than the sector if it isn't true"* | 1,2,3 | **3** | 7 | yes | yes | **fixed** — the mismatch is real and was deliberate; `audit_a`'s own docstring calls the band "an entire department-store sector", which is precisely what the chart never said. Subtitle now reads "one fulfilment network against whole department-store companies — a plausibility bound, not a peer target". **The strongest convergence in the panel: all three domain seats refused to repeat the finding until this was answered.** | 4.4 |
| 7 | *"This is 'both banners' — one blended number ... I'd bet money our order fill sits below the blend and Alder & Vance sits above it, and this chart lets that hide."* | 1,2,3 | **3** | 1,2,3,6,7 | yes | yes | **accepted** — charts 1 and 2 answer a definitional question (what does "fill" mean, and what does splitting buy) that is banner-independent, and the banner split is the whole subject of charts 4 and 5, where the decision is actually made. Accepted rather than dismissed: the seats are right that a banner-level fill series is absent from the module, and it is recorded as an open item below. | 0.1 |
| 8 | *"The gaps between ticks aren't equal so the slope of the fall is distorted, and the steepest-looking drop between $6 and $7 might just be the spacing."* — seat 4: *"Every slope in this chart is distorted."* | 2,4 | **2** | 5 | yes | yes | **fixed** — the x axis was a category axis carrying a continuous dollar quantity, so $8→$10 and $15→$20 occupied the same width as $5→$6. Now a value axis at true dollar positions. Note that seat 2 reached this from suspicion of the shape alone, without the vocabulary for it. | 2.1 |
| 9 | *"Store 104 and Store 103 are both $4.12 and drawn at identical height, presented inside an ordered ranking with no indication it's a tie"* — seat 2: *"I don't know if that's real or rounding"* | 2,4 | **2** | 6 | yes | yes | **accepted** — the tie is real to the cent ($4.117 and $4.119 before rounding) and the table carries the underlying units and parcel cost. Breaking the tie visually would assert a difference of two tenths of a cent. | 6.6 |
| 10 | *"the sector is rendered as a static band with no time dimension at all ... Half the title rests on data that isn't in the picture."* | 4 | 1 | 7 | yes | yes | **fixed** — the title's second clause was a comparison against an undrawn series. The real month-of-year Census shape was already in the payload and `audit_a`'s A3 test had been correlating against it the whole time. Now plotted as a dashed second series; its December trough (1.39) sits directly under the network's. Band and line are different adjustments and both now say so on the canvas. | 3.2 |
| 11 | *"If primary means Fernhill, double is $4.54 and no store clears it — claim false."* | 4 | 1 | 6 | yes | yes | **fixed** — the title's truth turned on which of two identically-coloured FCs was primary, and the chart did not say. The axis now marks Cascade Ridge FC as primary. A single-seat finding that invalidated a headline. | 3.2 |
| 12 | *"the achieved unit-fill series is gold in chart 1 and green in chart 2. A reader moving between the two will not recognize it as the same series."* | 4 | 1 | 2 | yes | yes | **fixed** — the same unit-fill series was drawn in two colours, breaking the fixed-slot rule stated at the top of the chart source itself. Chart 2 now draws it in Lichen, as chart 1 does. | 2.3.1 |
| 13 | *"two solid same-weight lines converging, hue-only"* | 4 | 1 | 5 | yes | yes | **fixed** — Alder & Vance is now dashed. The three categorical charts carried decal as a second channel and passed the programmatic check; this line chart had no non-colour channel at all and the check did not look for one. | 2.3.6 |
| 14 | *"a non-round top tick jammed against the last regular one. It reads as a bug, not a decision."* | 4 | 1 | 1,2,4 | yes | yes | **fixed** — axis bounds now snap to the gridline interval, so 73/75 and 95/99 become 70 and 100. | 6.6 |
| 15 | *"the title rounds 3.55% to '4%' while the label on the bar says 3.55%"* | 4 | 1 | 4 | yes | yes | **fixed** — title now carries the same two decimals as the marks. | 2.9 |
| 16 | *"The 'Alder & Vance' in-plot label sits directly on top of the green line near $6–$7"* | 4 | 1 | 5 | yes | no | **fixed** — series names now sit over the $7–$8 plateau, where no steep segment runs through them. Scored not-novel: pre-panel note 8 predicted annotation/mark collisions generally. | 3.4 |
| 17 | *"The bottom annotation's second line, 'series does,' runs into the 0.0 gridline and axis labels."* | 4 | 1 | 7 | yes | no | **fixed** — hung from 0.52 instead of 0.34. Not novel for the same reason as 16. | 3.4 |
| 18 | *"Three category points with two co-rising series is co-movement, nothing more ... it's asserted twice."* | 4 | 1 | 3 | yes | yes | **accepted** — the causal claim does not rest on the three bars. Slow movers are ranged at two nodes and fast movers at six by a documented policy in `generator_assumptions.md`, which is an input to the data rather than an inference from it, and the subtitle states it. Accepted rather than fixed because the alternative is to weaken a claim the module can actually support; recorded as an open item, because the seat is right that the plot alone does not carry it. | 3.2 |
| 19 | *"'Uses two nodes' reads at first glance as a label for B's blue bar specifically rather than for the blue series. I looked twice at that."* | 4 | 1 | 3 | yes | yes | **accepted** — the two series names are deliberately placed on different groups. Labelled on the same group they centre on adjacent bars and overlap into an unreadable smear, which is how the previous render shipped (defect A12's fix). Any single-group direct label carries this ambiguity; the alternative carried a worse one. | 3.6 |
| 20 | *"The descriptive paragraph appears above the title ... If that text is meant for screen readers only, it's leaking into the visual render."* | 4 | 1 | all | yes | yes | **accepted** — it is not leaking; `.chart-summary` is a deliberately visible description, wired to the canvas through `aria-describedby`, at 13px in slate against an 18px bold serif title. Hiding it would remove content from sighted readers who use it. But the seat's underlying point stands — a flat axis recital is the first text on every block — and no rule currently covers where a Rule 5.2 description should sit relative to the finding. Recorded as an open item for the design system. | 5.2 |
| 21 | *"This is a service-benefit chart with no cost axis"* | 1,2,3 | 3 | 2 | no | — | **rejected** — a request for a different chart, not a misreading of this one. The cost of splitting is charts 4 and 5, and the page pairs them. No seat misread what chart 2 shows; all three wanted the trade on one canvas, which would require an axis the counterfactual cannot support. | — |
| 22 | *"the whole thing sits on a 73-99 axis, so the peak troughs look more dramatic than a 100-scale would show"* | 2 | 1 | 1 | no | — | **rejected** — Rule 2.1 permits truncation where the title makes a gap claim, which this title does, and every plotted value is inside the axis. The axis now ends at 100 as a side effect of finding 14. | — |
| 23 | *"it's a very thin chart — two bars, both labelled, is a sentence with axes"* | 4 | 1 | 4 | no | — | **rejected** — a preference. Two banners is the entire population of the comparison; the chart is thin because the finding is. | — |
| 24 | *"I'd also want cost per order rather than per unit, since store shipments tend to be one-liners."* | 1 | 1 | 6 | no | — | **rejected** — a scope request. Cost per unit is the certified metric in the register and the one the title claims; per-order cost is a different measure, and the table carries shipments and units for anyone deriving it. | — |
| 25 | *"the subtitle admits the counterfactual is 'evaluated on the inventory position before each allocation,' which I don't fully follow on first read"* | 2 | 1 | 2 | no | — | **rejected** — the phrase is precise and load-bearing: it is what stops the counterfactual being evaluated with hindsight, which is the objection seats 1 and 3 both raised. The table caption expands it. Shortening it would cost the guarantee. | — |

### 2.4 · Summary

```
PANEL: 4 seats, simulated · 7 charts · findings 25 · defects 20 · novel 16
       fixed 13 · accepted 7 · rejected 5 · multi-seat defects 9
       D = 2.86 defects/chart · N = 0.80 novel share · R = 0.20 rejected share
```

Computed by the skill's `panel_metrics.py` from `panel/findings.json`.

**This is not recorded as a pass.** Twenty defects on seven charts, sixteen of
them absent from the author's pre-panel notes, is the opposite of a pass — and
had the panel returned nothing it would have been recorded as "no findings"
rather than as certification.

### 2.5 · What the panel says about the author's own review

The charts the panel read were the **second** render — the one the author had
already found and fixed thirteen defects in. D = 2.86 and N = 0.80 against a
corrected artifact is the finding that matters most in this section: **a
careful author review, on charts he had genuinely looked at, still left four in
five of the panel's defects uncaught.**

Three of them invalidated a headline outright and none were visible to any
check the build ran. The title of chart 4 asserted a shared cost that was an
order-weighted blend of two different costs. The title of chart 6 could not be
evaluated at all, because the chart withheld which of two FCs was primary. Half
the title of chart 7 rested on a series that was not drawn. All three survived
the author's review, and all three were found by readers who could see nothing
but the picture.

The single-seat findings were disproportionately the sharpest. The
visualization seat produced 13 of the 20 defects; the three domain seats
produced 7 between them, but those 7 include the three highest-consensus items
on the list and the one the module would have been most embarrassed to ship —
the sector comparison at finding 6. This matches the ratio the skill warns
about from the Deal Desk panel, and is now the second module in a row where the
canvas-only seat carried roughly two-thirds of the defect count. **One more
module at this ratio and the domain floor should drop from three to two**, per
the skill's own change-log instruction. Recorded here so that decision is made
on evidence rather than on the next panel's mood.

### 2.6 · Open items the panel raised that no fix closes

1. **No banner-level fill series exists in the module** (finding 7). Three seats
   asked for it independently and the honest answer is that it was never built.
2. **The causal claim on chart 3 rests on a documented ranging policy, not on
   the plot** (finding 18). True, defensible, and not visible.
3. **Rule 5.2 descriptions render above the finding** (finding 20). A design
   system question, not a Control Tower one.
4. **Chart 2 and chart 5 cannot be read together on one canvas** (finding 21).
   Rejected as a defect, but three seats wanting the same missing thing is the
   signal the skill says to weight above any single objection.

---

## 3 · Rule 7.3 scored checklist

`(rule, class, weight, evidence)` for every violation that survives. **Rescored
after the §2 panel**, against the shipping render.

| Rule | Class | Weight | Evidence | Status |
|---|---|---|---|---|
| 3.2 | INVARIANT | — | Chart 4's annotation says "near-identical **dollar cost**" over a plot whose only axis is percent of margin. The dollar figures are in the title and the data table, not on the marks. | **Accepted, and materially narrowed by the panel.** The prior version of this row accepted a title that read "the same $5.46 second parcel"; panel finding 3 established that $5.46 was an order-weighted blend of $5.64 and $5.18 and that "the same" was false. The title now names both figures, so the annotation's "near-identical" is checkable against the title even though neither is a mark. What survives is the original violation only: a dollar quantity claimed on a percent axis. |
| 3.2 | INVARIANT | — | Four headline figures — 7.0 points, 2.7 points, $5.46, 0.97 months — cannot be located on any mark, and four of four panel seats sourced them to the title. | **Accepted** under the computed-aggregate exception; see panel finding 1 for the full reasoning and why a reference line would be worse. Promoted from unrecorded to recorded: the author's own review did not catch this and the checklist did not previously carry it. |
| 2.9 | PREFERENCE | 4 | Bar value labels carry two decimals (`17.07%`, `12.09%`) where the rounding rule asks for three significant figures. | **Accepted, weight 4.** The two-decimal form is what makes the 4.1× and 2.1× ratios in the titles checkable against the marks. Rounding to `17%` and `4%` would break Rule 3.2 to satisfy a weight-4 preference. |

**PREFERENCE total: 4. INVARIANT violations: 0** — both 3.2 entries are accepted
against a stated exception rather than outstanding.

Everything else on the explanatory checklist passes. Verified programmatically
against the live DOM: no legend on any chart (every series directly labelled),
all seven carry a real data table wired through `aria-describedby`, all 138
table headers scoped, sequential heading order, no text below 12px, every text
colour ≥4.5:1, decal as a second non-colour channel on all three categorical
charts **and dash on both two-series line charts** (chart 5's dash was added by
panel finding 13 — it was the one chart with no non-colour channel at all, and
this programmatic sweep had not been looking for one on line charts), keyboard
navigators on the three time series whose finding is a shape, one provenance
strip per chart at exactly four segments, and no horizontal scroll at 320px.

**Read that list with panel finding 20 in mind.** Every item on it passed on
render 1 as well, the render with clipped data and a chart whose two series
could not be told apart. It is evidence about structure, not about legibility.

---

## 4 · Author's own review (Rule 7.1, author half)

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

## 5 · Second-arrangement note

Charts 1 and 2 were re-read with the axis floor removed, which is the arrangement
change Rule 7.1 asks for. It changed the reading materially: with the floor at
82% the three fill series looked like three flat, parallel, well-behaved lines
and the module's story was carried entirely by the title. With the floor removed
the November collapse dominates the plot, and the seasonal failure — which the
generator produces and the page never previously showed — becomes the visible
feature. **The corrected chart makes an argument the clipped one could not.**

---

## 6 · Renders

Three renders exist and the distinction matters for reading this document.

| Render | State | Where |
|---|---|---|
| 1 | Never reviewed by anyone. Thirteen defects, five fatal to a claim | not kept |
| 2 | Author's thirteen fixes applied. **This is what the four blind seats read** | `panel/charts/` |
| 3 | Panel's thirteen fixes applied. What ships | `panel/charts-postfix/` |

`panel/charts/` is deliberately **not** re-rendered. It is the evidence the
disposition table quotes against, and overwriting it would leave the review
citing readings of images that no longer exist.

Render 3 has not been panelled. That is the normal state — a panel reads what
was in front of it — but it means the thirteen fixes in §2.3 are the author's
work again, unread by anyone blind, and they carry exactly the confidence that
implies. Two of them changed a chart's structure rather than its labelling
(chart 5's axis type, chart 7's added series), which is where a fix is most
likely to introduce something new.

**If this module is extended or its charts materially change, the panel runs
again on the new render.** A panel result is about an artifact, not about a
module.

---

## 7 · A1 · Responsive review (2026-08-09)

**Viewports reviewed: 390×844, 414×896, 768×1024, 1440×900.** Previous sections
of this review were conducted at 1006px only. A chart reviewed at one width has
not been reviewed, so this section supersedes the Layer 5 portion of §3.

### What was wrong

Every chart overrode the shared theme's grid margins with fixed pixel values —
`left` at 52–62 against the theme's 8, discarding the point of `containLabel`,
which is to let ECharts compute the axis allowance from the labels it actually
draws. On a 292px phone canvas the worst chart gave the plot **30% of the
width and 55% of the height**.

### What changed

| Change | Effect |
|---|---|
| `left: 8` with `containLabel: true` on all seven | The axis allowance is computed, not guessed |
| **Title and subtitle moved out of the canvas into the DOM** | A canvas title reserves a fixed box sized for the widest case — 99px of a 290px canvas — and wraps to five lines at phone width anyway. In the DOM it reflows and grows the block downward. Plot height went from 52–61% to **72–85%** |
| Direct-label gutters measured, not typed | `measureGutter` runs the real font against the real label strings. One named constant per chart, collected in one place so the v2.3 amendment can replace the mechanism cleanly |
| `bottom` inherited via `containLabel` | The 40–76px overrides are gone; ECharts sizes for the labels each chart actually has, including the wrapped two-line node names |
| Axis tick interval `'auto'` | A fixed every-third-tick rule is a desktop measurement in disguise: eight month labels fit across 1006px and collided into an unreadable smear across 156px. Rule 5.5's drop order asks for thinning, never rotation |
| Annotation wrap width fixed at 190px | `cascadiaAnnotation` centres its label on a data coordinate, so a box wider than the plot overhangs the canvas. At 390px the counterfactual annotation lost its first two characters and read *"e gap is the fill splitting buys"* |
| `TOP_PAD` 34px | With the title gone this clears the annotations, which live in the reserved headroom at the top of each axis. At 8px it looked right in code and clipped the top line of every two-line annotation |

### Measured plot width, as a share of canvas

| Chart | 390px | 414px | 768px | 1440px |
|---|---|---|---|---|
| `c-vel` | 80.9% | 82.2% | 90.8% | 93.8% |
| `c-econ` | 80.9% | 82.2% | 90.8% | 93.8% |
| `c-thr` | 80.9% | 82.2% | 90.8% | 93.8% |
| `c-nodes` | 79.1% | 80.5% | 89.9% | 93.2% |
| `c-fills` | **64.0%** | 66.4% | 82.6% | 88.2% |
| `c-cf` | **49.3%** | **52.8%** | 75.5% | 83.5% |
| `c-inv` | **48.9%** | **52.4%** | 75.3% | 83.3% |

Also verified at every width: no horizontal page scroll; no stale canvas after
**resize without reload**; and opening a data table above a chart re-lays out
the chart below it (moved 837px, all charts still correctly sized).

### Three charts miss the 65% floor at 390px, and the reason is arithmetic

`c-fills` at 64.0% is one point short. `c-cf` and `c-inv` sit near 49%.

All three are the charts carrying **end-of-line direct labels**, and the floor
is unreachable for them without changing the labels themselves:

```
canvas at 390px viewport            328px
65% plot floor                      213px
left inset, containLabel            ~39px
  -> maximum affordable gutter       76px

c-fills   "Order fill"               73px   clears at 414px, 1pt short at 390
c-cf      "Single node only"        121px   45px over
c-inv     "Sector, unadjusted"      136px   60px over
```

The gutters are already minimal for the text they hold — they are measured
against the rendered font, not estimated. Closing the remaining gap requires
either shortening the label text at all widths, which makes the desktop chart
worse to serve the phone, or a width-aware label mechanism. **Both are the v2.3
amendment, which this task is explicitly scoped out of** (A1 §2.4). The gutters
are therefore left as named constants in one place, which is what A1 asked for,
so v2.3 can replace the mechanism without hunting through the file.

**All three remain readable at 390px** — series distinguishable, labels legible,
annotations intact, nothing clipped. They are narrow, not broken. Recorded as a
known limit rather than reported as a pass.

### The data tables (Rule 5.1 layer 2)

The charts were only half the narrow-screen problem. Five of the eight tables
overflowed their container at 390px — `tbl-econ` at 1.63× and the metric
register at 1.38× — and scrolled sideways inside a 328px box with no cue that
they did.

The useful pattern: **every table that is too wide is short, and every tall
table already fits.** The wide ones are 3–11 rows; the three 24-row tables are
4–5 columns and fit at 328px.

So the wide tables **stack into labelled rows below 560px** — each row becomes a
card with its label as a heading and `data-label` printing each column name
beside its value. The tall ones are left as tables. Above 560px nothing changes
at all: desktop renders exactly the table it did before.

Underneath that, all tables gained **scroll shadows** — pure-CSS, using
`background-attachment: local`, so the cue appears only on the side with more
content and disappears once a table fits — and a **sticky first column** below
860px so the row label stays in view while scrolling sideways.

**Every element carries an explicit ARIA role.** `display: block` is what makes
stacking work and it also strips a table's implicit semantics out of the
accessibility tree. These tables are the non-visual route to the data, so a
mobile layout that quietly stopped them being tables would trade a layout
problem for an accessibility regression. Redundant roles are normally a smell;
here they are what survives the display change.

Two defects found by rendering rather than by reading the CSS: a `caption` left
as `table-caption` inside a `display: block` table gets wrapped in an anonymous
box that shrinks to fit and renders **one word per line**; and the register's
reason column is prose rather than a figure, so it needed to read as a paragraph
under its label instead of as a right-aligned value.

Verified at 390, 559, 561, 768 and 1440: the breakpoint flips cleanly, no table
overflows its container at 390, and the page does not scroll sideways at any
width.

### Not done, deliberately

The general responsive rule (A1 §2.4), label abbreviation, a legend fallback and
a breakpoint system are all out of scope and were not written. No second resize
handler was added; the existing `ResizeObserver` plus window listener were
verified working and left alone. The Rule 7.4 panel was **not** re-run — that
decision sits with Aaron and belongs after v2.3.
