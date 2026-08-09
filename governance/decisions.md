# Decisions memo

**2026-08-09.** Every definitional call made during the build, in one place, so
Aaron can overturn any of them without reading the code.

The addendum's arrangement was that the agent decides, documents as it goes, and
Aaron reviews at the end. This is that review list. Each entry says what was
decided, why, and what it would cost to reverse. Where a decision is already
approved, it says so.

---

## Already approved by Aaron

| # | Decision | Status |
|---|---|---|
| 1 | Subject named **Alder & Vance Retail Group**; premium banner **Alder & Vance**, off-price **Off-Main**. Both invented; checked against live retail | Approved 2026-08-07 |
| 2 | The calibration filer is **never named**, and the page describes calibration in the plural — "published department-store filings" | Approved |
| 3 | Realism audit B **bounds** rather than matches, because fulfilment cost is not separately disclosed by any public department store | Approved |
| 4 | Warehouse ships as **DuckDB**; BigQuery and Looker Studio are a named, gated Phase 2 | Approved |
| 5 | Push only once `validate.py` was green and the reading panel recorded | Approved |
| 6 | Case-study `.qmd` drafted here, published from a site-rooted session | Approved |

---

## Decided by the agent — open to reversal

### Naming and disclosure

**7 · The calibration filer's raw XBRL bundle is not committed, and its CIK is
not in the repository.** The mechanism lives in `src/derive_calibration.py`,
which reads the identifier from an environment variable and refuses to run
without it. Only derived, unattributed ratios are committed.
*Cost of this decision:* that one input is **attested rather than reproducible**,
which breaks the portfolio's pull-once-freeze-commit principle for a single
source. *To reverse:* commit the bundle and the naming rule falls.

**8 · Realism audit A also bounds rather than matches**, for the same class of
reason as audit B but a different one in substance. Census inventories cover
entire department stores whose stock sits on selling floors this module never
simulates, so the network's 0.97 months against a sector band of 2.03–3.64 is
correct, not a miss. The audit requires the series to sit strictly inside the
band, clear a floor, and move with the real series seasonally (+0.62).
*To reverse:* nothing else works — a like-for-like level comparison is not
available at this scope, and forcing one would mean inventing a scaling factor.

### Metric definitions

**9 · A split is defined by NODE count, not parcel count.** Split-by-parcel is
retained as exploratory. Node count responds to the allocation decision under
review; parcel count also responds to carton sizing, which is a different
problem with a different owner.

**10 · `not_shipped` is a third classification state**, not folded into
single-node. An order that shipped nothing cannot be split or not-split.

**11 · Order fill is certified; line and unit fill retained as exploratory.**
Order fill is the only one that matches what the customer experiences.
*To reverse:* one line in `dbt/models/marts/_marts.yml` and a rebuild — the
register regenerates from that file.

**12 · Not-shipped orders stay in every fill denominator, and are excluded from
cost per order.** They are demand the network failed to serve; an order with no
parcel has no parcel cost.

**13 · Split premium is measured incrementally** — actual parcel cost minus what
the same shipped units would have cost in one parcel — not as split-average
versus single-node-average. Split orders are systematically larger baskets, so
the average-versus-average comparison compares two populations and flatters the
split.

### Generator

**14 · Inventory is held at style AND size; an order line is a style.** This is
what lets the three fill rates differ at all. Held at style level, every line is
all-or-nothing and unit fill and line fill collapse to within half a point.
*To reverse:* the three-numbers story goes with it.

**15 · Slow movers are ranged at two nodes, not one.** At one node a slow mover
can only ever be short, never split — the opposite of the behaviour under study.

**16 · Two independent levers.** Weekly demand volatility produces shortfall;
node cover asymmetry produces splits. A single lever cannot set both to
realistic values at once.

**17 · Four BLS occupations, not the one the brief names.** SOC 53-7062 remains
the headline anchor; 53-7065, 43-5071 and 53-1047 are marked supporting. A DC is
not staffed by one occupation.

**18 · The counterfactual is evaluated against the inventory position BEFORE
each real allocation commits**, so it is a genuine alternative history rather
than a comparison against already-depleted stock.

**19 · The Census band excludes March–May 2020.** Store closures drove the
department-store ratio to 6.16, **50.04** and 7.61 as the sales denominator
collapsed. A band containing 50.04 cannot be failed by any generator. The three
months are shown and named on the page rather than dropped silently.

### Presentation

**20 · Chart titles, axis bounds and accessibility summaries are all computed
from the data**, never typed. Hard-coded axis bounds clipped real values off two
charts, and hard-coded summaries stated ranges that were simply wrong.

**21 · The $4 threshold is omitted from chart 5's plot**, kept in its table and
in `validate.py`. Every split clears one extra parcel base rate, so both banners
sit at exactly 100% there, which forces a 0–100 axis and squashes the
informative range into the bottom fifth. Named in the subtitle and the
provenance flag. *Four of four panel seats noticed the omission and accepted the
reason.*

**22 · Darkened same-hue "text inks" for label and annotation text.** Three of
the five Cascadia palette hues fail WCAG 1.4.3 as text on Paper — Glacier 3.55,
Lichen 3.92, Madrona 4.31 — while passing the 3:1 that applies to marks. Marks
keep the full hue; only text darkens.
**This is a finding about the design system, not about this module.** It affects
any module using the direct labels the system mandates, and is the one item here
worth carrying back to `VIZ-PRINCIPLES.md`.

### Repository

**23 · The GitHub repo is `cascadia-controltower`, without the `-analytics`
suffix the local folder carries.** A project Pages site serves at
`www.robbinsanalytics.com/<repo-name>/`, so the repo name is the published URL
and `CLAUDE.md` specifies `/cascadia-controltower/`. Deal Desk and
semiconductors match; staffing does not, so the convention is not universal —
the target URL settles it.

**24 · The reproducibility hash is pinned to the generator's own tables.** dbt
writes into the same DuckDB file, so a hash over "whatever tables exist" would
report a reproducibility failure that was really just the warehouse rebuilding.

---

## Targets missed, and reported missed

**25 · The unit-fill target was missed at the first attempt and the world was not
forced to hit it.** The generator aimed for a three-point gap between unit and
line fill and produced 0.55. Three ways to force it were tried and rejected —
larger order quantities (baskets of 3.9 units per size, not a department store),
thinner stock everywhere (lowered all three metrics together without separating
them), a higher record-error rate (11% of picks, which describes a crisis).
Moving to size-level inventory fixed it properly: the gap is now 2.65 points and
the realized figures are 94.25 / 91.60 / 87.22 against targets of 94 / 91 / 87.

**26 · Definition-of-done item 6 remains unmet.** There is no live BigQuery or
Looker Studio view because there is no cloud project. Said plainly on the page.

---

## Still open

- **The shipping render has not been panelled.** The panel read render 2; render
  3 carries thirteen fixes made by the author in response, unread by anyone
  blind. Two changed a chart's structure rather than its labelling.
- **The prose has never been panelled.** Four seats read seven images. The
  surrounding page text states the findings in its own words and no blind reader
  has seen it.
- **Four panel items are closed by no fix**, recorded in `chart-review.md` §2.6.
