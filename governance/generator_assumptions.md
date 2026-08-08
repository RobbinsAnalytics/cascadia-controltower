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
| Unit fill | 94.0% | **94.25%** | +0.25 |
| Line fill | 91.0% | **91.60%** | +0.60 |
| Order fill | 87.0% | **87.22%** | +0.22 |
| Split rate | *no target* | 11.61% | — |
| Counterfactual unit fill, single-node rule | *no target* | 91.60% | — |

The three fill rates are targeted because they are the module's thesis: one
distribution centre reporting **94% to Operations, 92% to the merchant team and
87% to Finance**. Split rate carries no target on purpose — it is a free outcome
of inventory position and the allocation rule, and inventing a target for it and
then tuning until it was hit would make the split rate evidence of nothing except
that it had been dialled in. Realism audit C checks that splitting is
*concentrated and directional*, which is a claim about structure, not level.

### Why the three numbers can differ at all

Unit fill separates from line fill only through **partially** filled lines: a
line shipping four of six units is a failure to line fill but two-thirds of a
success to unit fill. An earlier version of this generator held stock at style
level, which made every line all-or-nothing — and unit fill and line fill came
out within 0.55 points of each other, the same number wearing two names.

**Stock is therefore held at style *and size*.** A line is a style and a
quantity; the units spread across the size run; the warehouse has to find each
size separately. Size brokenness is the commonest reason a real retail line ships
incomplete, and modelling it moved the unit-to-line gap from 0.55 points to 2.65
without touching a single fill-rate parameter.

The line could not simply be grained at size instead. Three units of a style is
an ordinary basket; three units of *one size* of one style is a wholesale order.
Reaching the target that way required mean quantities above four units per size,
which no department store sees.

---

## 2 · Calibration sources

| Input | Value | Source |
|---|---|---|
| Labor rates | $22.95/hr median, $18.87 p10, $30.00 p90 | **BLS OEWS May 2025**, SOC 53-7062, area 42660 Seattle-Tacoma-Bellevue. Frozen in `data/raw/oesm25ma.zip`. |
| Order-filler rate | $22.52/hr median | BLS OEWS, SOC 53-7065, same area |
| Clerk rate | $27.10/hr median | BLS OEWS, SOC 43-5071, same area |
| Inventory/sales behaviour | 2.03–3.64 band | **US Census MRTS**, department stores, seasonally adjusted, 2015–2026 excluding the closure months |
| SG&A share of revenue | 23.7%–39.0% | **SEC EDGAR**, Macy's / Kohl's / Dillard's, FY2018+ |
| Inventory-to-revenue, YoY direction | `data/raw/calibration_envelope.json` | One real department-store filer, **deliberately unattributed** — see `naming_policy.md` |

**The three March–May 2020 observations are excluded from the Census band** and
shown on the page rather than dropped silently. Store closures drove the
department-store inventories/sales ratio to 6.16, **50.04** and 7.61 as the sales
denominator collapsed. A band containing 50.04 cannot be failed by any generator,
and an audit that cannot fail is not an audit.

---

## 3 · Assortment and demand

| Parameter | Value | Rationale |
|---|---|---|
| Styles per banner | 1,200 | 2,400 styles, exploding to **8,640 style-size SKUs** |
| Category mix | Apparel 40%, Footwear 20%, Accessories 15%, Home 15%, Beauty 10% | A department-store assortment; the first two carry size runs |
| Size runs | Apparel XS–XL, Footwear 6–11, others one-size | Demand skewed to middle sizes, as it is in reality |
| Velocity mix (A/B/C) | 20% / 30% / 50% of styles | Standard ABC shape |
| Demand share (A/B/C) | 70% / 22% / 8% | Pareto concentration, drawn per **style** — customers want a style and then need their size, so drawing popularity at size level would smear the tail and remove the thin-bin problem |
| Unit value, premium | $88 mean, $34 sd | Sets the banner economics behind the second finding |
| Unit value, off-price | $26 mean, $9.50 sd | ~3.4× gap |
| Slow-mover value skew | B ×1.12, C ×1.34 | Slow movers skew expensive — part of why they are slow, and what makes a slow line worth rescuing with a second parcel |
| Gross margin | 38.5% premium, 30.2% off-price | Within the peer-filed range |
| Mean lines per order | 1.85 | Sets the line-to-order gap: `order_fill ≈ line_fill ^ lines_per_order` |
| Mean units per line | 2.83, across 1.64 sizes | Roughly 1.7 units per size — an ordinary basket |
| Weekly demand shock | lognormal, σ 0.45, mean 1 | Replenishment plans against average demand, so a style running hot for a week outruns its plan. **This is the lever that produces shortfall.** |

**Category is assigned from the position within each velocity band, not across
the whole assortment.** Using the global index made the bands come out sorted by
category — fast movers all apparel, slow movers all one-size goods — which would
have confounded velocity with sizing and handed the module a finding that was
really an artefact of style numbering.

---

## 4 · Network and inventory

| Parameter | Value | Rationale |
|---|---|---|
| Nodes | 6 — 2 FCs, 4 stores | Ship-from-store is how department stores actually fulfil |
| Stocking breadth (A/B/C) | 6 / 4 / **2** nodes, decided per style | A node ranges a style and its whole size run, not individual sizes |
| Cover held, premium / off-price | 1.86 / 1.38 weeks | Off-price runs leaner, so it stocks out more, so it splits more — a consequence of policy, never a rule about banners |
| Safety stock (A/B/C) | 0.55 / 0.40 / 0.30 weeks | Thinner for slow movers |
| Node cover multiplier | FC1 0.86, FC2 1.00, store 1.18 | The primary FC turns fastest and is run lean; stores hold selling stock sized for footfall. **This is the lever that produces splits.** |
| Replenishment | **(s, S) policy** — reorder when on-hand plus on-order falls to the reorder point, order up to target | See below |
| Reorder point | (lead time + review period + safety stock) weeks of demand | |
| Lead times | FC1 5 days, FC2 6 days, stores 3 days | Stock arrives on the day it lands, not the day it is ordered |
| Store fulfilment buffer | 2 units held back, 45% of the rest exposed | A store's stock is selling stock; not all of it is available to ship |
| Record-error rate | 7% of picks, per node | The system says five, the bin holds three. Phantom units are written off as an inventory adjustment so the ledger still balances. |
| Shrink | 0.11% of on-hand monthly | Keeps the conservation identity exercised |

### Two bugs found here, both worth recording

**Lead time did nothing.** The first version raised on-hand on the day stock was
*ordered* while crediting the ledger on the day it *arrived*. Lead time was a
documented parameter with no effect, and any month where an order straddled the
boundary closed negative — 10,186 sku-months did. Stock now sits in transit and
lands on its arrival date, and reordering works against inventory *position*
(on-hand plus on-order) so the same shortfall is not ordered again at every
review.

**The reorder trigger was a magic number.** It fired at a flat 60% of the
order-up-to level, which happened to sit just below lead-time-plus-review demand,
so every replenishment arrived slightly too late. Fill collapsed for a reason
that had nothing to do with the inventory being thin. It is now stated in weeks
of demand, as an inventory planner would state it.

### Two independent levers, on purpose

Demand volatility drives **shortfall**; node cover asymmetry drives **splits**.
They are separate because a single lever cannot set both — every attempt to lower
fill by thinning stock also raised the split rate, and the two could not be
brought to realistic values at the same time.

### Slow movers are stocked at two nodes, not one

At a single node a slow mover can only ever be **short** — there is no second
node to rescue it from. The thinnest-stocked segment would then short constantly
and split never, the precise opposite of the behaviour under study. At two nodes
the same thin stock produces both outcomes from one cause:

| Velocity band | Lines shipping zero | Lines shipping partial | Lines using >1 node |
|---|---|---|---|
| A (fast) | 2.0% | 4.4% | 4.2% |
| B | 4.5% | 8.4% | 10.2% |
| **C (slow)** | 3.7% | **9.5%** | **17.1%** |

Shortfall and splitting rise together across the bands. That co-occurrence is the
module's central claim, and it is observable here rather than asserted.

---

## 5 · Cost model

| Parameter | Value | Rationale |
|---|---|---|
| Parcel base cost | $4.35 | Per parcel, any node |
| Parcel cost per unit | $0.62 | |
| Store pick penalty | $1.85 | Stores pick slower and pack worse than an FC |
| Units per labor hour | receiving 142, putaway 96, picking 68, packing 54, shipping 128 | Picking and packing are the constraint, as in a real DC |

Labor is costed at the frozen BLS medians by function — a real regional wage, not
an invented rate.

### The split premium

Split cost is measured as the **incremental** cost of fragmenting a given order:
actual parcel cost minus what the same shipped units would have cost in one
parcel. Split orders are systematically larger baskets, so comparing the average
cost of split orders against the average cost of single-node orders compares two
different populations and **flatters the split**.

---

## 6 · What the run produced

| | Off-price (Off-Main) | Premium (Alder & Vance) |
|---|---|---|
| Split rate | 12.14% | 10.88% |
| Unit fill | 94.32% | 94.14% |
| Unit fill if splitting were forbidden | 91.65% | 91.52% |
| Average split premium | $5.64 | $5.18 |
| Average gross margin per split order | $71.73 | $249.31 |
| **Split premium as share of gross margin** | **12.09%** | **3.55%** |

**Splitting buys about 2.65 points of unit fill in both banners, and costs 3.4×
more of the margin in off-price than in premium.** That asymmetry is the second
finding, and no rule in the generator produces it — it falls out of unit value.

Totals over 24 months: **379,979 orders · 621,942 lines · $248,933 split
premium**, 8.58% of all parcel spend.

| Table | Rows |
|---|---|
| `dim_style` | 2,400 |
| `dim_sku` (style × size) | 8,640 |
| `fact_order` | 379,979 |
| `fact_order_line` | 621,942 |
| `fact_shipment` | 423,989 |
| `fact_receipt` | 484,045 |
| `fact_inventory_month` | 705,024 |
| `fact_labor_day` | 2,810 |

---

## 7 · Reproducibility

Same seed, same content hash — recorded in `generator_run.json` and re-checked
by `validate.py`.

The hash is over table **content**, not over the DuckDB file. Storage-engine
internals are not the claim being made; the data is. Two identical datasets
written by different DuckDB versions should agree, and they would not if file
bytes were hashed.

**Current content hash:** `6592611ba17db74bc0201f297742f9fa562ef1304dbdb70e43136d59940aec17`
