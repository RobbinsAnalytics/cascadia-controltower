"""
conform_anchors.py — govern the three frozen anchors into tidy, analysis-ready data.

Cascadia Control Tower · anchor conform

Input  : data/raw/*  (frozen and committed by ingest_anchors.py)
Output : data/clean/anchor_labor.csv       BLS OEWS wage percentiles
         data/clean/anchor_inventory.csv   Census department-store monthly series
         data/clean/anchor_peers.csv       peer annual figures + derived ratios
         governance/tag_mapping.csv        which XBRL tag actually won, per peer

WHAT THIS IS FOR
----------------
These three files are what the realism audits check the generator against. They
are derived from committed bytes only — this script makes no network call, and
neither does anything downstream of it.

THE RULES THIS ENFORCES
-----------------------
* **Missing is a first-class value.** Nothing is interpolated, zero-filled or
  estimated. Where a peer does not file a concept, the row says so and is
  flagged, and every downstream consumer must handle it.
* **Tag priority, not tag assumption.** No single us-gaap tag serves all three
  peers — Macy's has no `CostOfRevenue`, Dillard's has no `InventoryNet`. Each
  concept has an ordered candidate list; the winning tag per peer is written to
  governance/tag_mapping.csv so the drift is visible rather than absorbed.
* **Latest filed wins.** Restatements are real. Where the same fiscal year end is
  reported more than once, the most recently *filed* value is kept.

Adapted from cascadia-semiconductors-analytics/src/conform.py, simplified to
annual grain because this module benchmarks a cost *share*, not a quarterly path.

Usage:
    python src/conform_anchors.py
"""

import csv
import io
import json
import zipfile
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
CLEAN_DIR = REPO_ROOT / "data" / "clean"
GOV_DIR = REPO_ROOT / "governance"

# ---------------------------------------------------------------------------
# Anchor A — BLS OEWS
# ---------------------------------------------------------------------------

OEWS_AREA = "42660"          # Seattle-Tacoma-Bellevue, WA
OEWS_MEMBER = "oesm25ma/MSA_M2025_dl.xlsx"   # NOT BOS_ — see ingest_anchors.py

# 53-7062 is the anchor the brief names and the one cited on the page. The other
# three are the rest of a real DC's wage structure; a fulfillment centre is not
# staffed by one occupation, and costing every function at one rate would be a
# modelling shortcut the module elsewhere refuses to take.
OEWS_OCCUPATIONS = {
    "53-7062": ("material_mover", "anchor"),
    "53-7065": ("order_filler", "supporting"),
    "43-5071": ("shipping_receiving_clerk", "supporting"),
    "53-1047": ("supervisor", "supporting"),
}

WAGE_COLS = ["H_PCT10", "H_PCT25", "H_MEDIAN", "H_PCT75", "H_PCT90",
             "A_MEDIAN", "TOT_EMP"]


def conform_labor() -> pd.DataFrame:
    """Extract the Seattle-metro wage rows for the DC occupations."""
    zf = zipfile.ZipFile(RAW_DIR / "oesm25ma.zip")
    df = pd.read_excel(io.BytesIO(zf.read(OEWS_MEMBER)), dtype=str)
    df.columns = [c.upper() for c in df.columns]

    rows = []
    for soc, (role, tier) in OEWS_OCCUPATIONS.items():
        sel = df[(df["AREA"].astype(str).str.strip() == OEWS_AREA)
                 & (df["OCC_CODE"].astype(str).str.strip() == soc)]
        if len(sel) != 1:
            # Ambiguity fails the build. One area + one SOC must be one row.
            raise SystemExit(
                f"ERROR: expected exactly 1 OEWS row for area {OEWS_AREA} / SOC "
                f"{soc}, found {len(sel)}. Refusing to guess which one is meant."
            )
        r = sel.iloc[0]
        row = {"soc_code": soc, "role": role, "tier": tier,
               "occupation": r["OCC_TITLE"], "area": OEWS_AREA,
               "area_title": r["AREA_TITLE"], "vintage": "May 2025"}
        for c in WAGE_COLS:
            v = str(r[c]).strip()
            # BLS uses '*' and '#' for suppressed / above-cap values. Those are
            # gaps, and gaps are shown as gaps.
            row[c.lower()] = None if v in ("*", "#", "", "nan") else float(v)
        rows.append(row)
        print(f"  {soc} {role:24} median ${row['h_median']}/hr  "
              f"p10 ${row['h_pct10']}  p90 ${row['h_pct90']}")
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Anchor B — Census MRTS department stores
# ---------------------------------------------------------------------------

DEPT_STORE_NAICS = "4522"
SECTIONS = {
    "NOT ADJUSTED": ("inventories", "nsa"),
    "ADJUSTED(1)": ("inventories", "sa"),
    "INVENTORIES/SALES, RATIOS NOT ADJUSTED": ("inv_sales_ratio", "nsa"),
    "INVENTORIES/SALES, RATIOS ADJUSTED(1)": ("inv_sales_ratio", "sa"),
}
MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
          "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


def conform_inventory() -> pd.DataFrame:
    """Pull the department-store line out of every annual sheet.

    Sheet layout is stable 1992-2026: four stacked blocks, each headed by a
    section marker in column B, each containing one row per kind of business.
    Section markers are matched rather than row numbers hard-coded, because the
    2026 sheet is a partial year with a different footer length.
    """
    path = RAW_DIR / "mrtsinv92-present.xlsx"
    xl = pd.ExcelFile(path)
    records = []

    for sheet in xl.sheet_names:
        year = int(sheet)
        df = pd.read_excel(path, sheet_name=sheet, header=None, dtype=str)

        # Row 4 holds the month headers, e.g. 'Jan. 2024'.
        month_cols = {}
        for c in range(2, df.shape[1]):
            hdr = str(df.iloc[4, c]).strip()
            if hdr and hdr != "nan":
                mon = hdr.split(".")[0].split()[0][:3]
                if mon in MONTHS:
                    month_cols[c] = MONTHS[mon]

        section = None
        for i in range(len(df)):
            label = str(df.iloc[i, 1]).strip()
            if label in SECTIONS:
                section = SECTIONS[label]
                continue
            if section is None:
                continue
            if str(df.iloc[i, 0]).strip() != DEPT_STORE_NAICS:
                continue
            measure, adj = section
            for c, m in month_cols.items():
                raw = str(df.iloc[i, c]).strip()
                # (p) preliminary / (r) revised markers, and genuine blanks.
                cleaned = raw.replace("(p)", "").replace("(r)", "").strip()
                if cleaned in ("", "nan", "(NA)", "(S)"):
                    continue          # a gap stays a gap — no row is emitted
                records.append({
                    "year": year, "month": m,
                    "period": f"{year}-{m:02d}",
                    "naics": DEPT_STORE_NAICS,
                    "kind_of_business": "Department stores",
                    "measure": measure, "adjustment": adj,
                    "value": float(cleaned),
                    "preliminary": "(p)" in raw,
                })

    out = pd.DataFrame(records).sort_values(
        ["measure", "adjustment", "year", "month"]).reset_index(drop=True)
    ratios = out[(out.measure == "inv_sales_ratio") & (out.adjustment == "sa")]
    print(f"  {len(out):,} observations, {out.year.min()}-{out.year.max()}")
    print(f"  seasonally-adjusted inventories/sales ratio: "
          f"{ratios.value.min():.2f} to {ratios.value.max():.2f} "
          f"({len(ratios)} months)")
    return out


# ---------------------------------------------------------------------------
# Anchor C — SEC EDGAR peers
# ---------------------------------------------------------------------------

# Ordered candidates per concept. First tag that yields in-window annual data
# wins for that peer, and the winner is recorded in governance/tag_mapping.csv.
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
INSTANT_CONCEPTS = {"inventory"}     # balance-sheet items have no start date


def _fy_label(end_iso: str) -> int:
    """Retail fiscal years end in late Jan / early Feb of the FOLLOWING calendar
    year. FY2024 ends 2025-02-01. Shifting back six months lands the label in
    the year the business actually calls it."""
    return (date.fromisoformat(end_iso) - timedelta(days=180)).year


def _annual_points(facts: dict, tag: str, instant: bool) -> dict:
    """Return {fiscal_year_end: (value, filed, accn)} for annual 10-K values,
    latest filed winning any restatement."""
    node = facts.get("us-gaap", {}).get(tag)
    if not node:
        return {}
    out = {}
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
                continue          # not a full year — a quarter or a stub period
        end = pt["end"]
        prev = out.get(end)
        if prev is None or pt.get("filed", "") > prev[1]:
            out[end] = (pt["val"], pt.get("filed", ""), pt.get("accn", ""))
    return out


def conform_peers() -> tuple[pd.DataFrame, list]:
    manifest = json.loads((RAW_DIR / "manifest.json").read_text(encoding="utf-8"))
    peers = manifest["anchors"]["C_peers"]["companies"]

    rows, tag_rows = [], []
    for ticker, meta in peers.items():
        facts = json.loads(
            (RAW_DIR / meta["file"]).read_text(encoding="utf-8"))["facts"]

        # Resolve the winning tag PER FISCAL YEAR, not once per company.
        #
        # Tag drift runs in two directions and both are real. Across companies:
        # Dillard's reports inventory as RetailRelatedInventoryMerchandise while
        # the others use InventoryNet. Within a company, over time: Dillard's
        # moved revenue from `Revenues` to the ASC 606 tag, and cost of sales
        # from CostOfGoodsAndServicesSold to CostOfRevenue. Choosing one winner
        # for all years would silently discard years the filer really did
        # report — a gap manufactured by the pipeline rather than found in the
        # data, which is the opposite of showing gaps as gaps.
        series: dict = {}
        for concept, candidates in TAG_PRIORITY.items():
            per_year: dict = {}
            for tag in candidates:            # highest priority first
                for end, pt in _annual_points(
                        facts, tag, concept in INSTANT_CONCEPTS).items():
                    per_year.setdefault(end, (pt[0], pt[1], pt[2], tag))
            series[concept] = per_year
            used = sorted({v[3] for v in per_year.values()})
            if used:
                for tag in used:
                    yrs = sorted(_fy_label(e) for e, v in per_year.items()
                                 if v[3] == tag)
                    tag_rows.append([
                        ticker, meta["entity_name"], concept, tag, "filed",
                        f"FY{yrs[0]}-FY{yrs[-1]}" if len(yrs) > 1
                        else f"FY{yrs[0]}",
                        " > ".join(candidates)])
            else:
                tag_rows.append([ticker, meta["entity_name"], concept,
                                 "(not comparably tagged)", "missing", "-",
                                 " > ".join(candidates)])

        ends = sorted({e for pts in series.values() for e in pts})
        for end in ends:
            row = {"ticker": ticker, "entity_name": meta["entity_name"],
                   "fiscal_year_end": end, "fiscal_year": _fy_label(end)}
            for concept in TAG_PRIORITY:
                pt = series[concept].get(end)
                row[concept] = pt[0] if pt else None
                row[f"{concept}_tag"] = pt[3] if pt else None
                row[f"{concept}_missing"] = pt is None
            # Derived shares. Computed only where both inputs are present —
            # a missing input yields a missing ratio, never a zero.
            rev = row["revenue"]
            row["sga_pct_of_revenue"] = (
                round(row["sga"] / rev, 6)
                if rev and row["sga"] is not None else None)
            row["inventory_pct_of_revenue"] = (
                round(row["inventory"] / rev, 6)
                if rev and row["inventory"] is not None else None)
            rows.append(row)

        filed = sum(1 for c in TAG_PRIORITY if series[c])
        drift = sum(1 for c in TAG_PRIORITY
                    if len({v[3] for v in series[c].values()}) > 1)
        print(f"  {ticker:4} {meta['entity_name'][:26]:26} "
              f"{len(ends):>3} fiscal years · {filed}/4 concepts tagged"
              f"{f' · {drift} concept(s) drifted mid-history' if drift else ''}")

    return pd.DataFrame(rows).sort_values(["ticker", "fiscal_year_end"]), tag_rows


# ---------------------------------------------------------------------------

def main() -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    GOV_DIR.mkdir(parents=True, exist_ok=True)

    print("Anchor A — BLS OEWS, Seattle-Tacoma-Bellevue")
    labor = conform_labor()
    labor.to_csv(CLEAN_DIR / "anchor_labor.csv", index=False)

    print("\nAnchor B — Census MRTS, department stores")
    inv = conform_inventory()
    inv.to_csv(CLEAN_DIR / "anchor_inventory.csv", index=False)

    print("\nAnchor C — SEC EDGAR peers")
    peers, tag_rows = conform_peers()
    peers.to_csv(CLEAN_DIR / "anchor_peers.csv", index=False)

    with open(GOV_DIR / "tag_mapping.csv", "w", newline="",
              encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["ticker", "entity_name", "concept", "winning_tag",
                    "status", "fiscal_years_covered", "candidates_tried"])
        w.writerows(tag_rows)

    print(f"\nWrote {CLEAN_DIR / 'anchor_labor.csv'} ({len(labor)} rows)")
    print(f"Wrote {CLEAN_DIR / 'anchor_inventory.csv'} ({len(inv):,} rows)")
    print(f"Wrote {CLEAN_DIR / 'anchor_peers.csv'} ({len(peers)} rows)")
    print(f"Wrote {GOV_DIR / 'tag_mapping.csv'} ({len(tag_rows)} rows)")


if __name__ == "__main__":
    main()
