# Anchor verification

**Run 2026-08-07, before any generator design.** The brief requires that all three
real anchors be proven to pull *before* work is calibrated against them, so that a
substitution discovered late cannot invalidate work already done.

**Result: all three verified.** No substitutions were made. Two paths in the brief
were wrong and are corrected below.

---

## Anchor A — labor rates · BLS OEWS

**Source.** `https://www.bls.gov/oes/special-requests/oesm25ma.zip` (May 2025,
39,932,338 bytes). The metro file inside is `oesm25ma/MSA_M2025_dl.xlsx`
(150,023 rows, 32 columns).

> A trap worth recording: the archive's first workbook is `BOS_M2025_dl.xlsx` —
> *Balance of State*, the nonmetropolitan file. It contains SOC 53-7062 but no
> metro areas, so a naive read finds the occupation, finds no area 42660, and
> concludes the anchor is missing. The metro file is `MSA_`.

**The row.** Area 42660, SOC 53-7062, verified present exactly once:

| Field | Value |
|---|---|
| `AREA` / `AREA_TITLE` | 42660 · Seattle-Tacoma-Bellevue, WA |
| `OCC_CODE` / `OCC_TITLE` | 53-7062 · Laborers and Freight, Stock, and Material Movers, Hand |
| `TOT_EMP` | 29,490 |
| `H_PCT10` | $18.87 |
| `H_PCT25` | $20.87 |
| `H_MEDIAN` | $22.95 |
| `H_PCT75` | $26.48 |
| `H_PCT90` | $30.00 |
| `A_MEDIAN` | $47,740 |

The full percentile spread is present, which is what the brief requires — labor
cost sensitivity is modelled across the distribution, not at the median alone.
May-2024 and May-2023 vintages also resolve, so a prior-year comparison is
available if needed.

---

## Anchor B — inventory position · Census MRTS

**The brief's implied path does not exist.** `mrts/www/mrtsinv92-present.xls[x]`
returns 404. The file is published under a different directory:

**Source.** `https://www.census.gov/retail/mrtsinv/www/mrtsinv92-present.xlsx`
(245,266 bytes), reached from `https://www.census.gov/retail/mrtsinv/inventories.html`.

Titled *Estimates of End-of-Month Retail Inventories and Inventories/Sales Ratios
by Kind of Business*. 35 annual sheets, 1992 through 2026. **"Department stores"
confirmed present** as a kind-of-business line, carrying both the inventories
series and the inventories/sales ratio the realism audit needs.

Companion sales file, also verified:
`https://www.census.gov/retail/mrts/www/mrtssales92-present.xlsx`.

**Host discipline:** everything resolved on `www.census.gov`, which is on the
approved host list. The `api.census.gov` time-series API would have been easier
and was **not** used, because it is a host the brief does not authorise.

---

## Anchor C — P&L plausibility · SEC EDGAR

All three peer bundles pull from `data.sec.gov` under a compliant User-Agent.

| Ticker | CIK | Entity as filed | Bundle |
|---|---|---|---|
| M | 0000794367 | Macy's, Inc. | 3,756,173 bytes · 539 us-gaap tags |
| KSS | 0000885639 | KOHL'S CORP | 2,875,363 bytes · 427 us-gaap tags |
| DDS | 0000028917 | DILLARD'S, INC. | 2,812,563 bytes · 399 us-gaap tags |

### Tag drift is real and must be mapped

This is exactly the condition the reused semiconductors ingest exists to handle.
No single tag serves all three:

| Concept | Macy's | Kohl's | Dillard's |
|---|---|---|---|
| Revenue | `RevenueFromContractWithCustomerExcludingAssessedTax` | `RevenueFromContractWithCustomerExcludingAssessedTax` | `Revenues` |
| Cost of sales | `CostOfGoodsAndServicesSold` | `CostOfGoodsAndServicesSold` | `CostOfRevenue` |
| SG&A | `SellingGeneralAndAdministrativeExpense` | `SellingGeneralAndAdministrativeExpense` | `SellingGeneralAndAdministrativeExpense` |
| Inventory | `InventoryNet` | `InventoryNet` | **`RetailRelatedInventoryMerchandise`** |

`CostOfRevenue` is absent from Macy's entirely; `InventoryNet` is absent from
Dillard's entirely. A pipeline that assumed one tag per concept would silently
produce a two-company peer set and a realism audit with a hole in it.

### Realism audit B is reframed, and why

The brief asks audit B to check *fulfillment cost as a share of sales* against
peer XBRL. **Department stores do not tag fulfillment cost.** It is not a
separately reported concept in any of the three bundles; it sits inside SG&A and
cost of sales, undisclosed.

So audit B **bounds rather than matches**: modelled DC operating cost as a share
of net sales must fall inside the band implied by peer SG&A-to-sales. Verified
supportable — SG&A and revenue are both present for all three peers back to 2016
or earlier, so the band is computable from frozen data.

**This is a weaker claim than the brief assumed, and the page says so.** The
module states that fulfillment cost is not separately disclosed by any public
department store, so the audit constrains the model rather than confirming it.
Reported as a limit, not smoothed over. *(Approved 2026-08-07.)*

---

## Calibration source — status

Pulled by CIK for parameter calibration only; **not named here, not committed**,
per `naming_policy.md`.

Filing status confirms the calibration window is closed: Form 25-NSE filed
2025-05-21, Form 15-12G filed 2025-06-02, final reported fiscal year ending
**2025-02-01**. The entity no longer files. The envelope cannot drift.

Its ticker is absent from SEC's `company_tickers.json`, so — unlike the peer set,
whose CIKs are resolved from that committed map and never guessed — the
calibration pull cannot use the map. That pull is therefore performed outside the
repository and leaves no artifact in it.
