# Cascadia Control Tower

Distribution-centre analytics for **Alder & Vance Retail Group**, an invented
two-banner department-store fulfillment operation. Seventh module in the
[Cascadia portfolio](https://www.robbinsanalytics.com).

**Everything operational in this module is synthetic.** Every order, SKU,
shipment, labor hour and dollar was produced by a seeded generator. It
demonstrates a design; it measures nothing real. Three real public datasets do
the credibility work by constraining what the generator is allowed to produce.

---

## The thesis

A distribution centre reports **94% fill rate** to Operations, **87%** to Finance
and **91%** to the merchant team. Three numbers, three teams, all arithmetically
correct, none reconciled — because *order fill*, *line fill* and *unit fill* are
different metrics and nobody ever wrote down which one the business runs on.

Meanwhile the thing actually costing money is invisible in all three. **An order
split across two nodes still counts as filled.** It is 100% filled, on time, in
full — and costs roughly double to ship.

The definitional gap and the economic leak are the same phenomenon. Fill rate
looks healthiest exactly where splitting is worst, because splitting is *how* the
network achieves fill. The metric meant to measure service is concealing the cost
of delivering it.

The resolution is a governance act: certify one definition, retain the other two
as explicitly exploratory with a stated reason, and the leak becomes visible.

---

## The three real anchors

Pulled once, frozen, committed. **No build step and no published page makes a
network call.** Every realism audit is reproducible from the committed bytes, and
`data/raw/manifest.json` records a SHA-256 per file so a reader can prove it.

| Anchor | Source | What it constrains |
|---|---|---|
| **A · Labor** | BLS OEWS May 2025, SOC 53-7062, area 42660 Seattle-Tacoma-Bellevue | Units-per-labor-hour converts to dollars at real regional wages, across the percentile spread rather than at the median |
| **B · Inventory** | US Census MRTS, department stores, end-of-month inventories and inventories/sales ratios, 1992–2026 | The generator's inventory/sales ratio must land inside the real historical band |
| **C · P&L** | SEC EDGAR `companyfacts` — Macy's (M), Kohl's (KSS), Dillard's (DDS) | Modelled DC operating cost as a share of sales must sit inside the band real department stores report |

Anchor C is the module's step up from its predecessor. Cascadia Deal Desk
concedes that its generator imports its own matcher, so the pipeline is
consistent but not independently evidenced. Here the audits check the generator
against **real published financials** instead of against itself.

### What the anchors cost in honesty

- **Department stores do not disclose fulfillment cost.** It is not a separately
  tagged concept in any of the three filings; it sits inside SG&A and cost of
  sales. Audit B therefore **bounds** the model against peer SG&A-to-sales rather
  than matching a reported figure. That is a weaker claim than a match, and the
  page says so.
- **XBRL tags drift in two directions.** Across filers: Dillard's reports
  inventory as `RetailRelatedInventoryMerchandise` where the others use
  `InventoryNet`. Within a filer over time: all three moved revenue and cost of
  sales onto different tags mid-history. `governance/tag_mapping.csv` records
  every winning tag and the fiscal years it covers.
- **The Census series contains a real discontinuity.** March–May 2020 department
  store closures drove the inventories/sales ratio to 6.16, **50.04** and 7.61 as
  the sales denominator collapsed. Those months are shown, named, and excluded
  from the audit band with the reason stated — not quietly smoothed.

---

## Naming

The subject is invented. The premium banner is **Alder & Vance**, the off-price
banner is **Off-Main**. Macy's, Kohl's and Dillard's are named because they are
the real benchmark set doing the plausibility work — naming a benchmark is not
naming a subject.

The generator's calibration filer is **never named in this repository**, and only
derived, unattributed ratios enter it. See `governance/naming_policy.md`, which
records what that costs as well as what it protects.

---

## Layout

```
src/                  ingest, conform, generate, build
data/raw/             frozen source snapshots — committed, with SHA-256s
data/clean/           conformed anchors — committed
dbt/                  dbt Core project on DuckDB
governance/           the decisions, in writing
docs/                 the static ECharts page served by GitHub Pages
validate.py           the PASS/FAIL suite, including the three realism audits
```

## Reproducing

Run in this order. Only the first step touches the network, and it only needs
running once — `data/raw/` is committed.

```
python src/ingest_anchors.py                  # pull and freeze the anchors
python src/conform_anchors.py                 # govern them into data/clean
python src/generate.py                        # build the star schema
python validate.py --prove-failable           # 12 checks + audit failability
cd dbt && dbt build --profiles-dir . && cd .. # warehouse layer + 69 tests
python src/build_metric_register.py           # register, from dbt metadata
python src/build_metric_register.py --check    # fail if it has drifted
```

## The metric register is generated, not written

Every entry in `governance/metric_register.md` comes from a `meta:` block on a
column in `dbt/models/marts/_marts.yml` — the same file that defines that
column's tests. Change a definition, rebuild, and the register and the page
change with it.

`build_metric_register.py --check` regenerates in memory and compares against
what is committed, so a definition cannot quietly drift from the model that
computes it. **Eleven metrics: eight certified, three exploratory.**

Certification is not a ranking. An exploratory metric is not a bad metric; it is
one the business has agreed not to run on. Retaining the other definitions and
labelling them is the governance act — deleting them would move the
disagreement rather than resolve it.

## The warehouse layer

dbt Core 1.12 on DuckDB: 6 staging views, 9 marts, **69 data tests, all
passing.** The tests are a deliverable, not scaffolding — several encode
invariants that would otherwise be assumptions:

- inventory conservation on every SKU-node-month, no tolerance
- the stored classification must be re-derivable from shipments alone
- order fill can never exceed line fill — but unit-versus-line is deliberately
  **not** asserted, because that ordering depends on where shortfalls land and
  asserting it would encode an assumption as an invariant
- the single-node counterfactual can never beat what the network actually
  shipped
- split premium is never negative

BigQuery is a gated Phase 2. When the GCP project exists it becomes a second
output in `profiles.yml` and the models are unchanged — which is the point of
keeping transformation in dbt rather than in the page build.

## Build state

| Stage | Status |
|---|---|
| Anchor verification | Complete — `governance/anchor_verification.md` |
| Anchor freeze and conform | Complete |
| Generator and star schema | Complete — `governance/generator_assumptions.md` |
| `validate.py` and realism audits | Complete — **12/12 green** |
| dbt on DuckDB + metric register | Complete — **69/69 tests green**, 11 metrics |
| Static ECharts page | Not started |
| Reading panel | Not started |

The three fill rates the module is about, as generated:

| Metric | Value | Read by |
|---|---|---|
| Unit fill | **94.3%** | Operations |
| Line fill | **91.6%** | Merchant team |
| Order fill | **87.2%** | Finance |

One dataset, three arithmetics, three defensible answers, none reconciled.
Splitting buys 2.65 points of unit fill and costs 12.09% of gross margin in the
off-price banner against 3.55% in premium.

**The warehouse layer ships as DuckDB.** BigQuery and Looker Studio are a named,
gated Phase 2 awaiting a GCP project. The static page is the durable artifact and
survives without either.
