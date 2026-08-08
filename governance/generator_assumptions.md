# Generator assumptions

Every tunable that shapes the synthetic world, its value, why it holds that
value, and what the run actually produced. Seed `20260808`, 730 days,
2024-08-01 to 2026-07-31.

**Nothing in the operational data was measured anywhere.** The calibration
sources below constrain the *shape* of an invented world; they are not findings
and are never presented as such.

---

## 1 · Realized against target

| Metric | Target | Realized | Delta |
|---|---|---|---|
| Unit fill | 94.0% | **91.14%** | −2.86 |
| Line fill | 91.0% | **90.59%** | −0.41 |
| Order fill | 87.0% | **86.90%** | −0.10 |
| Split rate | *no target* | 10.00% | — |
| Counterfactual unit fill, single-node rule | *no target* | 87.70% | — |

### The unit-fill target was missed, and was not forced

Line fill and order fill land within half a point. Unit fill sits 2.9 points
below target, and the gap between unit fill and line fill is **0.55 points where
the target implied three**.

The reason is arithmetic, not tuning. Unit fill separates from line fill only
through **partially** filled lines — a line that ships four of six units is a
failure to line fill but two-thirds of a success to unit fill. Reaching a
three-point separation requires roughly 10% of all order lines to ship partially.
This run produces 4.0%, which is already at the high end of what an operation
with functioning replenishment would exhibit.

Three levers were tried and each was rejected:

- **Larger order quantities** widened the gap to about 1.2 points but pushed mean
  units per line to 3.9, which is not a department-store basket.
- **Thinner inventory everywhere** lowered all three metrics together without
  separating them, because a network-wide stockout ships zero rather than some.
- **A higher record-error rate** raised partial fills but had to reach 11% of
  picks, which would describe an operation in crisis rather than one with a
  measurement problem.

**So the target stands unmet and is reported unmet.** Forcing it would have meant
choosing an implausible world to make a headline number land, which is the
failure mode this module exists to criticise. The page reports 91% / 91% / 87%,
the numbers the simulation actually produced.

*Decision recorded 2026-08-08 and listed in `decisions.md` for review.*

---

## 2 · Calibration sources

| Input | Value | Source |
|---|---|---|
| Labor rates | $22.95/hr median, $18.87 p10, $30.00 p90 | **BLS OEWS May 2025**, SOC 53-7062, area 42660 Seattle-Tacoma-Bellevue. Frozen in `data/raw/oesm25ma.zip`. |
| Order-filler rate | $22.52/hr median | BLS OEWS, SOC 53-7065, same area |
| Clerk rate | $27.10/hr median | BLS OEWS, SOC 43-5071, same area |
| Inventory/sales behaviour | 2.03–3.64 band | **US Census MRTS**, department stores, seasonally adjusted, 2015–2026 excluding the closure months |
| SG&A share of revenue | 23.7%–39.0% | **SEC EDGAR**, Macy's / Kohl's / Dillard's, FY2018+ |
| Inventory-to-revenue, gross margin, YoY direction | see `data/raw/calibration_envelope.json` | One real department-store filer, **deliberately unattributed** — `naming_policy.md` |

**The three March–May 2020 observations are excluded from the Census band** and
shown on the page rather than dropped silently. Store closures drove the
department-store inventories/sales ratio to 6.16, **50.04** and 7.61 as the sales
denominator collapsed. A band containing 50.04 cannot be failed by any generator,
and an audit that cannot fail is not an audit.

---

## 3 · Assortment and demand

| Parameter | Value | Rationale |
|---|---|---|
| SKUs per banner | 1,200 | Enough for a long tail to exist without the run becoming a memory exercise |
| Velocity mix (A/B/C) | 20% / 30% / 50% of SKUs | Standard ABC shape |
| Demand share (A/B/C) | 70% / 22% / 8% | Pareto concentration; drawn per SKU so a fast mover is fast all year, not fast on average |
| Unit value, premium | $88 mean, $34 sd | Sets the banner economics that produce the second finding |
| Unit value, off-price | $26 mean, $9.50 sd | ~3.4× gap, the premium/off-price spread |
| Slow-mover value skew | B ×1.12, C ×1.34 | Slow movers skew expensive — it is part of why they are slow, and it is what makes a C-band line worth rescuing with a second parcel |
| Gross margin | 38.5% premium, 30.2% off-price | Within the peer-filed range |
| Mean lines per order | 1.49 | Sets the line-to-order fill gap; `order_fill ≈ line_fill ^ lines_per_order` |
| Mean units per line | 3.0 | Above one deliberately: a single-unit line is all-or-nothing and cannot separate unit fill from line fill |
| Weekly demand shock | lognormal, σ 0.45, mean 1 | Replenishment plans against average demand, so a SKU running hot for a week outruns its plan. **This is the lever that produces shortfall.** |

---

## 4 · Network and inventory

| Parameter | Value | Rationale |
|---|---|---|
| Nodes | 6 — 2 FCs, 4 stores | Ship-from-store is how department stores actually fulfil |
| Stocking breadth (A/B/C) | 6 / 4 / **2** nodes | See below |
| Cover held, premium / off-price | 2.10 / 1.55 weeks | Off-price runs leaner, so it stocks out more, so it splits more — a consequence of the policy, never a rule about banners |
| Safety stock (A/B/C) | 0.55 / 0.40 / 0.30 weeks | Thinner for slow movers |
| Node cover multiplier | FC1 0.86, FC2 1.00, store 1.18 | The primary FC is run lean because it turns fastest; stores hold selling stock sized for footfall. **This is the lever that produces splits.** |
| Store fulfilment buffer | 2 units held back, 45% of the rest exposed | A store's stock is selling stock. This is what makes partial line fills common. |
| Record-error rate | 7% of picks, per node | The system says five, the bin holds three. Phantom units are written off as an inventory adjustment so the ledger still balances. |
| Replenishment | Weekly review, reorder below 60% of target | Lead times 5 / 6 / 3 days |
| Shrink | 0.11% of on-hand monthly | Keeps the conservation identity exercised |

### Why slow movers are stocked at two nodes, not one

At a single node a slow mover can only ever be **short** — there is no second
node to rescue it from. The segment with the thinnest stock would then short
constantly and split never, which is the precise opposite of the behaviour under
study. At two nodes the same thin stock produces both outcomes from one cause,
and the co-occurrence the module is about becomes observable rather than
asserted.

The result is monotonic across the velocity bands, and it is the strongest
evidence the module has that splitting and shortfall share a cause:

| Velocity band | Lines shipping zero | Lines shipping partial | Lines using >1 node |
|---|---|---|---|
| A (fast) | 4.3% | 1.3% | 2.2% |
| B | 9.0% | 7.8% | 10.2% |
| **C (slow)** | 6.7% | **15.6%** | **25.4%** |

### Two independent levers, on purpose

Demand volatility drives **shortfall**; node cover asymmetry drives **splits**.
They are separate because a single lever cannot set both: every attempt to lower
fill by thinning stock also raised the split rate, and the two could not be
brought to realistic values at the same time.

---

## 5 · Cost model

| Parameter | Value | Rationale |
|---|---|---|
| Parcel base cost | $4.35 | Per parcel, any node |
| Parcel cost per unit | $0.62 | |
| Store pick penalty | $1.85 | Stores pick slower and pack worse than an FC |
| Units per labor hour | receiving 142, putaway 96, picking 68, packing 54, shipping 128 | Picking and packing are the constraint, as in a real DC |

Labor is costed at the frozen BLS medians by function. The run produced **93,032
hours and $2,161,741 of labor cost, a blended $23.24/hour** — a real regional
wage, not an invented rate.

### The split premium

Split cost is measured as the **incremental** cost of fragmenting a given order:
actual parcel cost minus what the same shipped units would have cost in one
parcel.

This matters. Split orders are systematically larger baskets, so comparing the
average cost of split orders against the average cost of single-node orders
compares two different populations and **flatters the split**. Measured
incrementally, holding basket contents fixed, the leak is unambiguous.

---

## 6 · What the run produced

| | Off-price (Off-Main) | Premium (Alder & Vance) |
|---|---|---|
| Split rate | 10.72% | 9.00% |
| Unit fill | 90.59% | 92.03% |
| Unit fill if splitting were forbidden | 87.10% | 88.68% |
| Average split premium | $5.90 | $5.08 |
| Average gross margin per split order | $62.75 | $222.38 |
| **Split premium as share of gross margin** | **14.07%** | **3.74%** |

**Splitting buys about 3.4 points of unit fill in both banners, and costs 3.8×
more of the margin in off-price than in premium.** That asymmetry is the second
finding, and no rule in the generator produces it — it falls out of unit value.

Totals over 24 months: 381,127 orders · 569,592 lines · **$223,067 split premium**,
8.17% of all parcel spend.

| Table | Rows |
|---|---|
| `fact_order` | 381,127 |
| `fact_order_line` | 569,592 |
| `fact_shipment` | 410,578 |
| `fact_receipt` | 206,909 |
| `fact_inventory_month` | 195,840 |
| `fact_labor_day` | 2,810 |

---

## 7 · Reproducibility

Same seed, same content hash — recorded in `generator_run.json` and re-checked
by `validate.py`.

The hash is over table **content**, not over the DuckDB file. Storage-engine
internals are not the claim being made; the data is. Two identical datasets
written by different DuckDB versions should agree, and they would not if file
bytes were hashed.

**Current content hash:** `7e0408127793b5b36403571db87c9675211f9425dfc04da30553d50ec196c1c8`
