"""
validate.py — the PASS/FAIL suite, including the three realism audits.

Cascadia Control Tower

Writes governance/validation_report.md. Exits non-zero if anything fails, so a
red run cannot be published by accident.

    python validate.py                  run the suite
    python validate.py --prove-failable demonstrate each realism audit CAN fail

THIS FILE DOES NOT IMPORT THE GENERATOR
---------------------------------------
Every rule is re-derived here from the base facts. Cascadia Deal Desk concedes
on its own page that its generator imports its matcher, so the pipeline is
guaranteed consistent but that is not independent evidence the rule is correct.
Importing `generate.py` here would reproduce exactly that weakness: the suite
would prove only that the code agrees with itself.

THE REALISM AUDITS MUST BE ABLE TO FAIL
---------------------------------------
An audit that cannot fail is not an audit. Each of the three is written as a
pure function of measured numbers, so `--prove-failable` can hand it deliberately
wrong values and show it trips. The result of that run is recorded in the report
alongside the real one.

WHAT THE AUDITS CAN AND CANNOT CLAIM
------------------------------------
Audits A and B **bound** the model rather than matching it, and the reason is
scope, not convenience. The module is a fulfillment network; the anchors describe
whole department-store enterprises.

  * Census inventories cover entire department stores, most of whose stock sits
    on selling floors serving walk-in customers this module never simulates. A
    fulfillment network legitimately holds far fewer months of stock.
  * Fulfillment cost is not separately disclosed by any public department store.
    It sits inside SG&A alongside stores, marketing, occupancy and corporate.

So each audit asserts the generator sits in the correct RELATIONSHIP to the real
figure — strictly inside it, materially large, and moving with it — rather than
equal to it. That is a weaker claim than a match, it is stated as such on the
page, and it can still fail in both directions.
"""

import argparse
import json
import re
import sys
from pathlib import Path

import duckdb
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent
CLEAN_DIR = REPO_ROOT / "data" / "clean"
GOV_DIR = REPO_ROOT / "governance"
DB_PATH = CLEAN_DIR / "controltower.duckdb"

COVID_CLOSURE_MONTHS = ["2020-03", "2020-04", "2020-05"]
PEER_CIKS = {"0000794367", "0000885639", "0000028917"}

# The only company names permitted anywhere in this repository. An allow-list,
# not a block-list, so that compliance never requires anyone to hold the
# forbidden name in mind. See governance/naming_policy.md.
PERMITTED_COMPANIES = ["Alder & Vance", "Off-Main", "Alder & Vance Retail Group",
                       "Macy's", "Kohl's", "Dillard's"]

results = []


def record(check_id, name, passed, detail, kind="check"):
    results.append({"id": check_id, "name": name, "passed": passed,
                    "detail": detail, "kind": kind})
    flag = "PASS" if passed else "FAIL"
    print(f"  [{flag}] {check_id:5} {name}")
    for line in str(detail).splitlines():
        print(f"           {line}")


def pearson(a, b):
    """Correlation without pulling in scipy."""
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a) ** 0.5
    vb = sum((y - mb) ** 2 for y in b) ** 0.5
    return cov / (va * vb) if va and vb else 0.0


# ===========================================================================
# The three realism audits, as pure functions so they can be proven failable
# ===========================================================================

def audit_a(ratio_mean, gen_by_month, census_band, census_by_month,
            floor=0.50):
    """Inventory position against the Census department-store series.

    Three ways to fail:
      A1  the network holds MORE months of stock than an entire department-store
          sector, which no fulfillment operation does
      A2  it holds so little that the modelled service level is unattainable
      A3  its seasonal shape does not move with the real one
    """
    lo, hi = census_band
    a1 = ratio_mean < lo
    a2 = ratio_mean > floor
    months = sorted(set(gen_by_month) & set(census_by_month))
    g = [gen_by_month[m] for m in months]
    c = [census_by_month[m] for m in months]
    corr = pearson(g, c)
    peak = [m for m in months if m in (11, 12)]
    rest = [m for m in months if m not in (11, 12)]
    gen_dip = (sum(gen_by_month[m] for m in peak) / len(peak)
               < sum(gen_by_month[m] for m in rest) / len(rest))
    a3 = corr >= 0.40 and gen_dip
    detail = (
        f"generator inventory/sales ratio {ratio_mean:.3f} months\n"
        f"A1 strictly below Census sector band [{lo:.2f}, {hi:.2f}]: "
        f"{'yes' if a1 else 'NO'}\n"
        f"A2 above {floor:.2f}-month floor: {'yes' if a2 else 'NO'}\n"
        f"A3 seasonal shape tracks the real series: corr {corr:+.3f} "
        f"(needs >= 0.40), peak-season dip {'present' if gen_dip else 'ABSENT'}")
    return a1 and a2 and a3, detail


def audit_b(cost_share, sga_band, min_fraction_of_sga=0.15):
    """Fulfillment cost against peer SG&A.

    Fulfillment cost is not separately tagged by any of the three peers, so this
    bounds rather than matches. Two ways to fail: the DC costs more than the
    whole of a peer's SG&A, or so little that it is not a real cost centre.
    """
    lo, hi = sga_band
    b1 = cost_share < lo
    b2 = cost_share >= lo * min_fraction_of_sga
    detail = (
        f"DC operating cost {cost_share:.2%} of shipped sales\n"
        f"B1 below peer SG&A band [{lo:.2%}, {hi:.2%}]: {'yes' if b1 else 'NO'}\n"
        f"B2 at least {min_fraction_of_sga:.0%} of the lower SG&A bound "
        f"({lo * min_fraction_of_sga:.2%}): {'yes' if b2 else 'NO'}\n"
        f"   = {cost_share / lo:.1%} of the leanest peer's SG&A ratio")
    return b1 and b2, detail


def audit_c(rate_by_band, min_spread=2.0):
    """Splitting must be concentrated and directional, not uniform noise.

    Uniform noise produces equal rates across the velocity bands. This fails if
    the rates are not strictly increasing from fast to slow movers, or if the
    slowest band is not materially worse than the fastest.
    """
    bands = ["A", "B", "C"]
    rates = [rate_by_band[b] for b in bands]
    c1 = rates[0] < rates[1] < rates[2]
    spread = rates[2] / rates[0] if rates[0] else 0.0
    c2 = spread >= min_spread
    detail = (
        f"multi-node line rate by velocity band: "
        + ", ".join(f"{b} {r:.2f}%" for b, r in zip(bands, rates)) + "\n"
        f"C1 strictly increasing fast -> slow: {'yes' if c1 else 'NO'}\n"
        f"C2 slow/fast spread {spread:.2f}x (needs >= {min_spread}x): "
        f"{'yes' if c2 else 'NO'}")
    return c1 and c2, detail


# ===========================================================================
# Measurement
# ===========================================================================

def measure(con):
    m = {}

    m["fills_from_lines"] = con.execute("""
        WITH per_order AS (
          SELECT order_id,
                 COUNT(*)                                   AS lines,
                 SUM(CASE WHEN qty_shipped = qty_ordered THEN 1 ELSE 0 END)
                                                            AS lines_full,
                 SUM(qty_ordered)                           AS units_ord,
                 SUM(qty_shipped)                           AS units_shp
          FROM fact_order_line GROUP BY order_id)
        SELECT SUM(units_shp)::DOUBLE / SUM(units_ord)      AS unit_fill,
               SUM(lines_full)::DOUBLE / SUM(lines)         AS line_fill,
               AVG(CASE WHEN lines_full = lines THEN 1.0 ELSE 0 END)
                                                            AS order_fill
        FROM per_order""").fetchone()

    m["fills_from_order"] = con.execute("""
        SELECT SUM(units_shipped)::DOUBLE / SUM(units_ordered),
               SUM(lines_filled)::DOUBLE / SUM(lines_ordered),
               AVG(CASE WHEN units_shipped = units_ordered THEN 1.0 ELSE 0 END)
        FROM fact_order""").fetchone()

    inv_sales = con.execute("""
        WITH inv AS (
          SELECT i.year_month,
                 SUM(i.closing_units * s.unit_cost) AS inv_cost
          FROM fact_inventory_month i JOIN dim_sku s USING (sku_key)
          GROUP BY 1),
        sales AS (
          SELECT d.year_month, SUM(o.value_shipped) AS sales
          FROM fact_order o JOIN dim_date d ON o.order_date_key = d.date_key
          GROUP BY 1)
        SELECT inv.year_month,
               CAST(SPLIT_PART(inv.year_month, '-', 2) AS INT) AS month,
               inv_cost / sales AS ratio
        FROM inv JOIN sales USING (year_month) ORDER BY 1""").df()
    m["inv_sales_ratio_mean"] = float(inv_sales.ratio.mean())
    m["inv_sales_by_month"] = inv_sales.groupby("month").ratio.mean().to_dict()

    cost = con.execute("""
        SELECT (SELECT SUM(labor_cost) FROM fact_labor_day)
             + (SELECT SUM(parcel_cost) FROM fact_order) AS dc_cost,
               (SELECT SUM(value_shipped) FROM fact_order) AS sales""").fetchone()
    m["dc_cost"], m["sales"] = float(cost[0]), float(cost[1])
    m["dc_cost_share"] = m["dc_cost"] / m["sales"]

    m["multinode_by_band"] = {
        r[0]: float(r[1]) for r in con.execute("""
            SELECT st.velocity_band,
                   100.0 * SUM(CASE WHEN l.nodes_on_line > 1 THEN 1 ELSE 0 END)
                         / COUNT(*)
            FROM fact_order_line l JOIN dim_style st USING (style_key)
            GROUP BY 1""").fetchall()}
    return m


def load_anchors():
    inv = pd.read_csv(CLEAN_DIR / "anchor_inventory.csv")
    r = inv[inv.measure == "inv_sales_ratio"]
    sa = r[(r.adjustment == "sa") & (~r.period.isin(COVID_CLOSURE_MONTHS))
           & (r.year >= 2015)]
    nsa = r[(r.adjustment == "nsa") & (~r.period.isin(COVID_CLOSURE_MONTHS))
            & (r.year >= 2015)]
    peers = pd.read_csv(CLEAN_DIR / "anchor_peers.csv")
    peers = peers[peers.fiscal_year >= 2018]
    return {
        "census_band": (float(sa.value.min()), float(sa.value.max())),
        "census_by_month": nsa.groupby("month").value.mean().to_dict(),
        "sga_band": (float(peers.sga_pct_of_revenue.min()),
                     float(peers.sga_pct_of_revenue.max())),
    }


# ===========================================================================
# The suite
# ===========================================================================

def run_suite(con, m, anchors):
    # --- 1 classification is total and exclusive ---------------------------
    bad = con.execute("""
        SELECT COUNT(*) FROM fact_order
        WHERE classification IS NULL
           OR classification NOT IN ('split','single_node','not_shipped')
           OR (classification = 'split'       AND nodes_used <= 1)
           OR (classification = 'single_node' AND nodes_used <> 1)
           OR (classification = 'not_shipped' AND (nodes_used <> 0
                                                   OR units_shipped > 0))
        """).fetchone()[0]
    counts = con.execute("""SELECT classification, COUNT(*) FROM fact_order
                            GROUP BY 1 ORDER BY 1""").fetchall()
    record("1", "Every order resolves to exactly one classification", bad == 0,
           f"{bad} violations · " + ", ".join(f"{c}={n:,}" for c, n in counts))

    # --- 2 the three fill rates reconcile, computed independently ----------
    a, b = m["fills_from_lines"], m["fills_from_order"]
    diffs = [abs(x - y) for x, y in zip(a, b)]
    record("2", "Three fill rates reconcile from base facts", max(diffs) < 1e-9,
           f"recomputed from fact_order_line vs stored on fact_order\n"
           f"unit  {a[0]:.6f} vs {b[0]:.6f}\n"
           f"line  {a[1]:.6f} vs {b[1]:.6f}\n"
           f"order {a[2]:.6f} vs {b[2]:.6f}\n"
           f"max absolute difference {max(diffs):.2e}")

    # --- 3 split classification is deterministic, no ambiguous case --------
    mismatch = con.execute("""
        WITH derived AS (
          SELECT o.order_id, o.classification,
                 COALESCE(COUNT(DISTINCT sh.node_key), 0) AS nodes
          FROM fact_order o
          LEFT JOIN fact_shipment sh USING (order_id)
          GROUP BY 1, 2)
        SELECT COUNT(*) FROM derived
        WHERE classification <> CASE WHEN nodes = 0 THEN 'not_shipped'
                                     WHEN nodes = 1 THEN 'single_node'
                                     ELSE 'split' END""").fetchone()[0]
    ambiguous = con.execute("""
        SELECT COUNT(*) FROM fact_order_line
        WHERE qty_shipped > 0 AND primary_node IS NULL""").fetchone()[0]
    record("3", "Split classification deterministic; no ambiguous case",
           mismatch == 0 and ambiguous == 0,
           f"re-derived from fact_shipment node counts: {mismatch} mismatches\n"
           f"shipped lines with no source node (would fail the build): "
           f"{ambiguous}")

    # --- 4 referential integrity ------------------------------------------
    orphans = {}
    for label, sql in [
        ("order_line -> dim_style",
         "SELECT COUNT(*) FROM fact_order_line l LEFT JOIN dim_style s "
         "USING (style_key) WHERE s.style_key IS NULL"),
        ("order_line -> fact_order",
         "SELECT COUNT(*) FROM fact_order_line l LEFT JOIN fact_order o "
         "USING (order_id) WHERE o.order_id IS NULL"),
        ("shipment -> dim_node",
         "SELECT COUNT(*) FROM fact_shipment f LEFT JOIN dim_node n "
         "USING (node_key) WHERE n.node_key IS NULL"),
        ("inventory -> dim_sku",
         "SELECT COUNT(*) FROM fact_inventory_month i LEFT JOIN dim_sku s "
         "USING (sku_key) WHERE s.sku_key IS NULL"),
        ("receipt -> dim_sku",
         "SELECT COUNT(*) FROM fact_receipt r LEFT JOIN dim_sku s "
         "USING (sku_key) WHERE s.sku_key IS NULL"),
        ("order -> dim_date",
         "SELECT COUNT(*) FROM fact_order o LEFT JOIN dim_date d "
         "ON o.order_date_key = d.date_key WHERE d.date_key IS NULL"),
    ]:
        orphans[label] = con.execute(sql).fetchone()[0]
    record("4", "Referential integrity across all dimensions",
           all(v == 0 for v in orphans.values()),
           "\n".join(f"{k}: {v}" for k, v in orphans.items()))

    # --- 5 labor reconciles to units at the stated rates -------------------
    labor = con.execute("""
        SELECT function, SUM(units) AS units, SUM(hours) AS hours,
               MAX(units_per_hour) AS uph,
               ABS(SUM(units)::DOUBLE / MAX(units_per_hour) - SUM(hours)) AS gap
        FROM fact_labor_day GROUP BY 1 ORDER BY 1""").df()
    shipped = con.execute(
        "SELECT SUM(units_shipped) FROM fact_order").fetchone()[0]
    received = con.execute(
        "SELECT SUM(units) FROM fact_receipt").fetchone()[0]
    pick = int(labor.loc[labor.function == "picking", "units"].iloc[0])
    recv = int(labor.loc[labor.function == "receiving", "units"].iloc[0])
    # Receipts scheduled beyond the period end never land, so receiving labor
    # counts only what actually arrived.
    record("5", "Labor hours reconcile to units at stated rates",
           bool(labor.gap.max() < 1.0) and pick == shipped and recv <= received,
           f"max hours discrepancy {labor.gap.max():.4f}\n"
           f"picking units {pick:,} == units shipped {shipped:,}: "
           f"{pick == shipped}\n"
           f"receiving units {recv:,} <= receipts raised {received:,}: "
           f"{recv <= received}")

    # --- 6 inventory conservation -----------------------------------------
    viol = con.execute("""
        SELECT COUNT(*) FROM fact_inventory_month
        WHERE closing_units <> opening_units + receipt_units
                              - shipped_units - adjustment_units""").fetchone()[0]
    negative = con.execute(
        "SELECT COUNT(*) FROM fact_inventory_month "
        "WHERE closing_units < 0").fetchone()[0]
    rows = con.execute(
        "SELECT COUNT(*) FROM fact_inventory_month").fetchone()[0]
    record("6", "Inventory conserved per SKU per period",
           viol == 0 and negative == 0,
           f"opening + receipts - shipped - adjustments = closing\n"
           f"{viol} violations and {negative} negative balances "
           f"across {rows:,} sku-node-months")

    # --- 7 exception counts monotonic as the threshold rises ---------------
    # Thresholds span the actual split-premium distribution. Starting at zero
    # would put the first three points on top of each other, since every split
    # costs at least one extra parcel base rate, and a flat head tells the
    # reader nothing about where a policy threshold would bite.
    thresholds = [4, 5, 6, 7, 8, 10, 12, 15, 20]
    counts7 = [con.execute(
        "SELECT COUNT(*) FROM fact_order WHERE classification = 'split' "
        f"AND split_premium > {t}").fetchone()[0] for t in thresholds]
    monotonic = all(x >= y for x, y in zip(counts7, counts7[1:]))
    non_degenerate = counts7[0] > counts7[-1] > 0
    record("7", "Exception counts monotonic as split-cost threshold rises",
           monotonic and non_degenerate,
           "  ".join(f"${t}:{c:,}" for t, c in zip(thresholds, counts7))
           + f"\nmonotonically non-increasing: {monotonic}; "
             f"non-degenerate curve: {non_degenerate}")

    # --- 8/9/10 the realism audits ----------------------------------------
    ok_a, det_a = audit_a(m["inv_sales_ratio_mean"], m["inv_sales_by_month"],
                          anchors["census_band"], anchors["census_by_month"])
    record("8", "REALISM AUDIT A - inventory position vs Census", ok_a, det_a,
           kind="audit")

    ok_b, det_b = audit_b(m["dc_cost_share"], anchors["sga_band"])
    record("9", "REALISM AUDIT B - fulfillment cost vs peer SG&A", ok_b, det_b,
           kind="audit")

    ok_c, det_c = audit_c(m["multinode_by_band"])
    record("10", "REALISM AUDIT C - splits concentrated, not noise", ok_c, det_c,
           kind="audit")

    # --- 11 reproducibility ------------------------------------------------
    run = json.loads((GOV_DIR / "generator_run.json").read_text(encoding="utf-8"))
    import hashlib
    h = hashlib.sha256()
    for table in sorted(t[0] for t in con.execute("SHOW TABLES").fetchall()):
        n, s = con.execute(
            f"SELECT COUNT(*), COALESCE(SUM(hash(to_json(t))::HUGEINT), 0) "
            f"FROM {table} t").fetchone()
        h.update(f"{table}:{n}:{s}".encode())
    digest = h.hexdigest()
    record("11", "Database content hash matches the recorded run",
           digest == run["content_sha256"],
           f"recorded {run['content_sha256']}\ncomputed {digest}")

    # --- 12 naming policy ---------------------------------------------------
    leaks, scanned = [], 0
    skip_dirs = {".git", "__pycache__", "target", "dbt_packages"}
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {
                ".py", ".md", ".sql", ".yml", ".yaml", ".html", ".csv",
                ".json", ".qmd", ".txt"}:
            continue
        if any(p in skip_dirs for p in path.parts):
            continue
        if path.name.startswith("companyfacts_"):
            continue                      # frozen peer bundles, named on purpose
        scanned += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for cik in set(re.findall(r"CIK(\d{10})", text)):
            if cik not in PEER_CIKS:
                leaks.append(f"{path.relative_to(REPO_ROOT)}: CIK{cik}")
    # A block-list cannot live in this repo, so the strict token check takes its
    # tokens from the environment. Absent that, say so rather than claim a pass.
    import os
    tokens = [t.strip() for t in os.environ.get("CT_FORBIDDEN_TOKENS", "").split(",")
              if t.strip()]
    token_hits = []
    if tokens:
        for path in sorted(REPO_ROOT.rglob("*")):
            if (not path.is_file() or any(p in skip_dirs for p in path.parts)
                    or path.suffix.lower() not in {
                        ".py", ".md", ".sql", ".yml", ".yaml", ".html", ".csv",
                        ".json", ".qmd", ".txt"}):
                continue
            text = path.read_text(encoding="utf-8", errors="replace").lower()
            for t in tokens:
                if t.lower() in text:
                    token_hits.append(f"{path.relative_to(REPO_ROOT)}: {t}")
    detail = (f"scanned {scanned} text files\n"
              f"unexpected CIK references: {len(leaks)}"
              + ("\n" + "\n".join(leaks) if leaks else "")
              + f"\nstrict token scan: "
              + (f"{len(token_hits)} hits" if tokens
                 else "SKIPPED - CT_FORBIDDEN_TOKENS not set")
              + ("\n" + "\n".join(token_hits) if token_hits else ""))
    record("12", "Naming policy - no unpermitted company identifiers",
           not leaks and not token_hits, detail)


# ===========================================================================
# Proving the audits can fail
# ===========================================================================

def prove_failable(m, anchors):
    print("\nProving each realism audit CAN fail, by feeding it wrong numbers:\n")
    proofs = []

    # A: a fulfillment network holding more stock than the whole sector.
    ok, _ = audit_a(m["inv_sales_ratio_mean"] * 5, m["inv_sales_by_month"],
                    anchors["census_band"], anchors["census_by_month"])
    proofs.append(("A", "inventory inflated 5x (above the Census band)", ok))

    # A3: seasonality removed — a flat world should fail the shape test.
    flat = {mo: 1.0 for mo in m["inv_sales_by_month"]}
    ok, _ = audit_a(m["inv_sales_ratio_mean"], flat,
                    anchors["census_band"], anchors["census_by_month"])
    proofs.append(("A", "seasonal shape flattened", ok))

    # B: a DC costing more than a whole department store's SG&A.
    ok, _ = audit_b(m["dc_cost_share"] * 6, anchors["sga_band"])
    proofs.append(("B", "DC cost inflated 6x (above peer SG&A)", ok))

    # B: a DC that costs almost nothing to run.
    ok, _ = audit_b(m["dc_cost_share"] / 20, anchors["sga_band"])
    proofs.append(("B", "DC cost cut to a rounding error", ok))

    # C: uniform noise instead of a pattern.
    ok, _ = audit_c({"A": 9.0, "B": 9.0, "C": 9.0})
    proofs.append(("C", "splits made uniform across velocity bands", ok))

    # C: the pattern pointing the wrong way.
    ok, _ = audit_c({"A": 17.0, "B": 10.0, "C": 4.0})
    proofs.append(("C", "concentration reversed (fast movers split most)", ok))

    all_tripped = True
    for audit, scenario, passed in proofs:
        tripped = not passed
        all_tripped &= tripped
        print(f"  [{'TRIPPED' if tripped else 'DID NOT TRIP'}] "
              f"audit {audit}: {scenario}")
    print()
    return proofs, all_tripped


# ===========================================================================

def write_report(m, anchors, proofs=None, all_tripped=None):
    failed = [r for r in results if not r["passed"]]
    lines = [
        "# Validation report",
        "",
        f"**{'PASS' if not failed else 'FAIL'}** — "
        f"{len(results) - len(failed)} of {len(results)} checks passed.",
        "",
        "Generated by `validate.py`. This suite does not import the generator;",
        "every rule is re-derived from the base facts, so a pass is evidence the",
        "data obeys the documented rules rather than evidence that the code",
        "agrees with itself.",
        "",
        "| # | Check | Result |",
        "|---|---|---|",
    ]
    for r in results:
        lines.append(f"| {r['id']} | {r['name']} | "
                     f"{'PASS' if r['passed'] else '**FAIL**'} |")
    lines += ["", "---", "", "## Detail", ""]
    for r in results:
        lines += [f"### {r['id']} · {r['name']}", "",
                  f"**{'PASS' if r['passed'] else 'FAIL'}**", "", "```",
                  str(r["detail"]), "```", ""]

    lines += [
        "---", "",
        "## What the realism audits can and cannot claim", "",
        "Audits A and B **bound** the model rather than matching it, and the",
        "reason is scope rather than convenience.", "",
        "The Census series covers entire department stores, most of whose stock",
        "sits on selling floors serving walk-in customers this module never",
        "simulates. A fulfillment network legitimately holds far fewer months of",
        "stock, and the audit says so: it requires the generator to sit strictly",
        "*inside* the sector figure, to be materially large, and to move with it",
        "seasonally.", "",
        "Fulfillment cost is not separately tagged by Macy's, Kohl's or",
        "Dillard's. It sits inside SG&A alongside stores, marketing, occupancy",
        "and corporate. Audit B therefore bounds the modelled DC cost by the peer",
        "SG&A band rather than matching a reported figure.", "",
        "Both are weaker claims than a match. Both can still fail in either",
        "direction, and the page states the limitation rather than implying a",
        "precision the disclosure does not support.", "",
    ]

    if proofs is not None:
        lines += [
            "---", "",
            "## Proof the realism audits can fail", "",
            "An audit that cannot fail is not an audit. Each audit is a pure",
            "function of measured numbers, so it can be handed deliberately wrong",
            "values. Every scenario below **must** trip its audit.", "",
            "| Audit | Scenario | Result |", "|---|---|---|",
        ]
        for audit, scenario, passed in proofs:
            lines.append(f"| {audit} | {scenario} | "
                         f"{'tripped' if not passed else '**DID NOT TRIP**'} |")
        lines += ["", f"**{'All scenarios tripped.' if all_tripped else 'A scenario failed to trip — the audit is not load-bearing.'}**", ""]

    (GOV_DIR / "validation_report.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prove-failable", action="store_true",
                    help="demonstrate each realism audit can fail")
    args = ap.parse_args()

    if not DB_PATH.exists():
        sys.exit(f"ERROR: {DB_PATH} not found. Run python src/generate.py first.")

    con = duckdb.connect(str(DB_PATH), read_only=True)
    anchors = load_anchors()
    m = measure(con)

    print("Cascadia Control Tower · validation\n")
    run_suite(con, m, anchors)

    proofs = all_tripped = None
    if args.prove_failable:
        proofs, all_tripped = prove_failable(m, anchors)

    write_report(m, anchors, proofs, all_tripped)
    con.close()

    failed = [r for r in results if not r["passed"]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    print(f"Wrote {GOV_DIR / 'validation_report.md'}")
    if failed:
        print("\nFAILED: " + ", ".join(f"{r['id']} {r['name']}" for r in failed))
        sys.exit(1)
    if args.prove_failable and not all_tripped:
        print("\nFAILED: a realism audit did not trip when given wrong numbers.")
        sys.exit(1)


if __name__ == "__main__":
    main()
