# Naming policy

**Decision taken 2026-08-07. Approved by Aaron Robbins.**

This module models a distribution centre. Distribution centres belong to
companies, and the company this module resembles is real. This file records how
that is handled, because the handling is a governance decision and not an
implementation detail.

---

## The subject is invented

| Entity | Name | Status |
|---|---|---|
| Operator | **Alder & Vance Retail Group** | Invented |
| Premium banner | **Alder & Vance** | Invented |
| Off-price banner | **Off-Main** | Invented |

Checked against live retail on 2026-08-07: no department store or off-price chain
trades under either banner name. The nearest name collisions are an unrelated
independent boutique and a department-store chain defunct since the 1980s,
neither of which is a two-banner fulfillment operation and neither of which is
referenced by this module.

**Every order, SKU, shipment, labor hour and dollar in this module was produced by
a seeded generator.** No operational figure here was ever measured anywhere.

## The calibration filer is never named

The generator's *scale and mix* parameters — inventory-to-sales behaviour, digital
share of sales, the shape of a dual-banner single-node network — are calibrated so
the synthetic operation is not absurd. That calibration draws on published
financial statements from a real, formerly-listed department-store operator.

**That company is not named in this repository and never will be.** Not on the
page, not in code, not in comments, not in filenames, not in commit messages, not
in `data/raw/`.

### What this costs, stated plainly

The portfolio's freeze principle is *pull once, freeze, commit the raw snapshot* —
so a reader can reproduce the audit against the same bytes. **For this one source,
that principle is deliberately broken.** The filer's raw XBRL bundle carries its
entity name and ticker in plain text; committing it would write the name into the
repo.

So:

- The raw bundle is pulled **outside the repository**, and is never staged.
  `.gitignore` blocks the path as a second line of defence.
- Only **derived, unattributed ratios** enter the repo, in
  `data/raw/calibration_envelope.json`. That file carries no entity name, no
  ticker, no CIK, and no accession number.
- The three **realism audits do not depend on it.** They check against the Census
  department-store series and the Macy's / Kohl's / Dillard's peer bundles, all of
  which are frozen and committed in full and are fully reproducible.

**The naming rule outranks the freeze rule.** The cost is that one input is
attested rather than reproducible. The benefit is that the rule holds without
exception. That trade is the decision.

### The calibration window is closed permanently

The filer deregistered in mid-2025 — Form 25-NSE filed 2025-05-21, Form 15-12G
filed 2025-06-02. Its final reported fiscal year ends **2025-02-01**. There is no
later data and there never will be. The calibration envelope is therefore frozen
by circumstance as well as by policy, and cannot silently drift.

## What the page says

**The page describes calibration in the plural** — "calibrated to published
department-store filings" — and never as a single unnamed filer.

This is deliberate. Naming one unnamed filer is a worse disclosure than naming
none: it tells the reader there is exactly one company to guess, and hands them
the category, the era and the structure to guess it with. The plural formulation
is true, since the peer set genuinely participates in bounding the model, and it
points at no one.

## Who may be named

| Permitted | Why |
|---|---|
| **Alder & Vance**, **Off-Main**, **Alder & Vance Retail Group** | Invented. They *are* the subject. |
| **Macy's, Kohl's, Dillard's** | The real XBRL benchmark set doing the plausibility work. Naming a benchmark is not naming a subject — the same standing as the seven named peers in Cascadia Finance. |
| **BLS, US Census Bureau, SEC / EDGAR, NRF** | Institutions and data publishers, not commercial subjects. |
| Software — DuckDB, dbt, Apache ECharts, BigQuery, Looker Studio, Quarto | Tools. |

**Any company name outside this table appearing anywhere in this repository is a
defect.** The check is an allow-list, not a block-list, precisely so that
compliance never requires anyone to hold the forbidden name in mind.
