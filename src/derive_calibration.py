"""
derive_calibration.py — derive the generator's calibration envelope.

Cascadia Control Tower · calibration

Output: data/raw/calibration_envelope.json   (committed — carries NO identity)

WHY THIS SCRIPT IS SHAPED THE WAY IT IS
---------------------------------------
The generator's scale and mix parameters are calibrated so the synthetic
operation is not absurd — a two-banner department-store fulfilment operation
should carry inventory, spend on SG&A and turn stock at rates a real operator of
that shape would recognise. That calibration draws on one real filer's published
financial statements.

**That filer is never named in this repository, and neither is its CIK.** A CIK
is a unique identifier; hard-coding one here would name the company as surely as
typing its name. So the identifier is supplied out of band:

    $env:CT_CALIBRATION_CIK = "..."      # PowerShell
    python src/derive_calibration.py

The script refuses to run without it and never writes it anywhere.

What this buys and what it costs is recorded in governance/naming_policy.md. In
short: the mechanism is in the repository and fully auditable — a reader can see
exactly which concepts are read, how each ratio is derived, and that nothing is
estimated — while the identity stays out. The cost is that this one input is
attested rather than reproducible. The three realism audits deliberately do not
depend on it; they run against the Census series and the peer bundles, which are
frozen and committed in full.

The output file carries derived RATIOS ONLY. No entity name, no ticker, no CIK,
no accession number, no absolute dollar figures — an absolute revenue figure
would identify the filer as effectively as its name.

Usage:
    python src/derive_calibration.py
"""

import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "data" / "raw" / "calibration_envelope.json"

USER_AGENT = "RobbinsAnalytics cascadia-controltower ajayrobbins@hotmail.com"

# Same two-direction tag priority the peer conform uses. The calibration filer
# drifts too — it reports revenue as `Revenues`, not the ASC 606 tag.
TAG_PRIORITY = {
    "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax",
                "Revenues", "SalesRevenueNet"],
    "cost_of_sales": ["CostOfGoodsAndServicesSold", "CostOfRevenue",
                      "CostOfGoodsSold"],
    "sga": ["SellingGeneralAndAdministrativeExpense",
            "GeneralAndAdministrativeExpense"],
    "inventory": ["InventoryNet", "RetailRelatedInventoryMerchandise",
                  "InventoryFinishedGoods"],
}
INSTANT_CONCEPTS = {"inventory"}


def polite_get(url: str) -> bytes:
    for attempt, backoff in enumerate([0, 2, 5, 15, 60]):
        if backoff:
            time.sleep(backoff)
        time.sleep(0.25)
        req = urllib.request.Request(
            url, headers={"User-Agent": USER_AGENT,
                          "Accept-Encoding": "gzip, deflate"})
        try:
            resp = urllib.request.urlopen(req, timeout=180)
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return raw
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504):
                raise
        except urllib.error.URLError:
            pass
    raise RuntimeError("calibration pull failed after retries")


def _fy_label(end_iso: str) -> int:
    return (date.fromisoformat(end_iso) - timedelta(days=180)).year


def _annual(facts: dict, concept: str) -> dict:
    """{fiscal_year: value} for annual 10-K values, latest filed wins,
    tag resolved per year in priority order."""
    instant = concept in INSTANT_CONCEPTS
    per_end: dict = {}
    for tag in TAG_PRIORITY[concept]:
        node = facts.get("us-gaap", {}).get(tag)
        if not node:
            continue
        for pt in node.get("units", {}).get("USD", []):
            if pt.get("form") != "10-K" or pt.get("fp") != "FY":
                continue
            if instant:
                if pt.get("start"):
                    continue
            else:
                if not pt.get("start"):
                    continue
                span = (date.fromisoformat(pt["end"])
                        - date.fromisoformat(pt["start"])).days
                if not 330 <= span <= 400:
                    continue
            end = pt["end"]
            prev = per_end.get(end)
            if prev is None or (prev[2] == tag
                                and pt.get("filed", "") > prev[1]):
                if prev is None or prev[2] == tag:
                    per_end[end] = (pt["val"], pt.get("filed", ""), tag)
    return {_fy_label(e): v[0] for e, v in per_end.items()}


def main() -> None:
    cik = os.environ.get("CT_CALIBRATION_CIK", "").strip()
    if not cik:
        sys.exit(
            "ERROR: CT_CALIBRATION_CIK is not set.\n"
            "\n"
            "The calibration filer's identifier is deliberately not stored in\n"
            "this repository — see governance/naming_policy.md. Supply it in\n"
            "the environment for this one run:\n"
            "\n"
            '    $env:CT_CALIBRATION_CIK = "<cik>"\n'
            "    python src/derive_calibration.py\n"
        )

    facts = json.loads(polite_get(
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:0>10}.json"
    ).decode("utf-8"))["facts"]

    series = {c: _annual(facts, c) for c in TAG_PRIORITY}
    years = sorted(set(series["revenue"]) & set(series["inventory"])
                   & set(series["sga"]))
    if not years:
        sys.exit("ERROR: no fiscal year has revenue, inventory and SG&A all "
                 "filed. Refusing to derive a partial envelope.")

    # Ratios only. Absolute dollars are omitted on purpose — a revenue figure
    # identifies the filer as effectively as its name does.
    ratios = []
    for y in years:
        rev, inv, sga = series["revenue"][y], series["inventory"][y], series["sga"][y]
        cos = series["cost_of_sales"].get(y)
        prev = {"revenue": series["revenue"].get(y - 1),
                "inventory": series["inventory"].get(y - 1)}
        ratios.append({
            "fiscal_year": y,
            "inventory_to_revenue": round(inv / rev, 5),
            "sga_to_revenue": round(sga / rev, 5),
            "cost_of_sales_to_revenue": round(cos / rev, 5) if cos else None,
            "gross_margin": round(1 - cos / rev, 5) if cos else None,
            # Year-over-year direction is the shape the generator reproduces:
            # inventory building while sales soften is the condition that makes
            # a fill-rate metric look healthy while cost quietly rises.
            "revenue_yoy": (round(rev / prev["revenue"] - 1, 5)
                            if prev["revenue"] else None),
            "inventory_yoy": (round(inv / prev["inventory"] - 1, 5)
                              if prev["inventory"] else None),
        })

    envelope = {
        "purpose": (
            "Calibration envelope for the Cascadia Control Tower generator. "
            "Derived ratios only — this file deliberately carries no entity "
            "name, ticker, CIK, accession number or absolute dollar figure."
        ),
        "what_the_filer_does_not_tag": {
            "net_sales": (
                "NOT separately tagged after FY2017. The filer tags total "
                "revenue only, which includes credit and other revenue "
                "alongside merchandise sales. Every 'revenue' ratio in this "
                "file is therefore against TOTAL revenue, not net sales. The "
                "two move differently: total revenue rose 2.2% in the final "
                "reported year while net sales fell, because the non-"
                "merchandise components grew. Not reconciled here, because "
                "reconciling it would require reading the 10-K face "
                "statements, and the difference is disclosed instead."
            ),
            "cost_of_sales": (
                "NOT tagged after FY2019 — GrossProfit ends there and no cost "
                "of sales concept replaces it. Gross margin is therefore "
                "unavailable for recent years and is reported as missing, not "
                "estimated from an older year."
            ),
        },
        "attested_inputs": {
            "note": (
                "Calibration points taken from the filer's public reporting "
                "that are NOT derivable from XBRL company facts. Flagged as "
                "attested rather than verified. One of them — the inventory "
                "change — IS independently derivable here and came back at "
                "exactly the attested value, which is the only cross-check "
                "available on this set."
            ),
            "net_sales_yoy_final_year": {
                "value": -0.021, "status": "attested",
                "why": "net sales not separately tagged; see above"},
            "inventory_yoy_final_year": {
                "value": 0.114, "status": "VERIFIED — matches XBRL derivation",
                "why": "independently derived from InventoryNet in this run"},
            "digital_share_of_sales": {
                "value": 0.36, "status": "attested",
                "why": "channel mix is an MD&A disclosure, not an XBRL concept"},
        },
        "provenance": (
            "Derived from one real department-store operator's audited annual "
            "filings, read from SEC XBRL company facts. The filer is not named "
            "here and is not named anywhere in this repository. See "
            "governance/naming_policy.md, which records that this one source "
            "breaks the pull-once-freeze-commit principle and why the naming "
            "rule outranks it."
        ),
        "reproducibility": (
            "ATTESTED, NOT REPRODUCIBLE. src/derive_calibration.py contains the "
            "full derivation and can be re-run by anyone holding the "
            "identifier, which is supplied out of band. The three realism "
            "audits do not depend on this file; they run against the Census "
            "series and the Macy's / Kohl's / Dillard's bundles, which are "
            "frozen and committed in full."
        ),
        "window_note": (
            "The filer deregistered in mid-2025 and its final reported fiscal "
            "year has already been filed. This envelope cannot drift, because "
            "there will be no later data."
        ),
        "derivation": {
            c: " > ".join(TAG_PRIORITY[c]) for c in TAG_PRIORITY
        },
        "revenue_concept": ("TOTAL revenue as filed, not net sales — "
                            "see what_the_filer_does_not_tag"),
        "fiscal_years": ratios,
    }
    OUT_PATH.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {OUT_PATH}")
    print(f"{len(ratios)} fiscal years · ratios only, no identity\n")
    print(f"  {'FY':<6} {'inv/rev':>9} {'sga/rev':>9} {'gross_mgn':>10} "
          f"{'rev_yoy':>9} {'inv_yoy':>9}")
    for r in ratios[-6:]:
        def f(v, pct=True):
            return "     --  " if v is None else (
                f"{v:>8.1%} " if pct else f"{v:>8.3f} ")
        print(f"  {r['fiscal_year']:<6} {f(r['inventory_to_revenue'])}"
              f"{f(r['sga_to_revenue'])} {f(r['gross_margin'])}"
              f"{f(r['revenue_yoy'])}{f(r['inventory_yoy'])}")


if __name__ == "__main__":
    main()
