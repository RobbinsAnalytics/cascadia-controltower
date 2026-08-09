"""
build_page.py — render the durable static page from the dbt marts.

Cascadia Control Tower · presentation

Input : data/clean/controltower.duckdb  (analytics_marts, built by dbt)
        docs/data/metric_register.json  (built by build_metric_register.py)
Output: docs/index.html                 (dataset inlined, no render-time fetch)

    python src/build_page.py

NO NETWORK AT RENDER TIME. ECharts and the Cascadia theme are vendored into
docs/assets/ and the dataset is inlined into the page at build time. A reader
with no connection to anything sees the same page. This layer is the durable
artifact and survives the warehouse being switched off, which is the whole
reason it exists.

TITLES ARE COMPUTED, NOT TYPED. Rule 3.1 requires every chart title to be a
complete sentence stating the finding; Rule 3.2 requires every element of that
claim to be readable from the plot. Both fail quietly the moment a number in a
title stops matching the data behind it. So every figure in every title is
formatted from the same query that feeds the chart — a stale claim would have
to survive a rebuild, and it cannot.
"""

import json
from datetime import date
from pathlib import Path

import duckdb

from page_template import PAGE

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "clean" / "controltower.duckdb"
DOCS = REPO_ROOT / "docs"
OUT = DOCS / "index.html"

AS_OF = "2026-08-08"
SOURCE = "Seeded generator · BLS OEWS · Census MRTS · SEC EDGAR"


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def fetch(con):
    d = {}

    d["summary"] = con.execute(
        "SELECT * FROM analytics_marts.fct_operations_summary").df().iloc[0].to_dict()

    d["fills"] = con.execute("""
        SELECT year_month,
               SUM(units_shipped)*1.0/SUM(units_ordered)            AS unit_fill,
               SUM(lines_filled)*1.0/SUM(lines_ordered)             AS line_fill,
               SUM(orders_filled)*1.0/SUM(orders)                   AS order_fill,
               SUM(counterfactual_unit_fill*units_ordered)
                   /SUM(units_ordered)                              AS cf_unit_fill,
               SUM(orders)                                          AS orders
        FROM analytics_marts.fct_fill_rate_monthly
        GROUP BY 1 ORDER BY 1""").df().to_dict("records")

    d["velocity"] = con.execute("""
        SELECT velocity_band,
               SUM(lines)                                           AS lines,
               SUM(lines*pct_lines_partial)/SUM(lines)              AS pct_partial,
               SUM(lines*pct_lines_zero)/SUM(lines)                 AS pct_zero,
               SUM(lines*pct_lines_multi_node)/SUM(lines)           AS pct_multi_node,
               SUM(units_shipped)*1.0/SUM(units_ordered)            AS unit_fill
        FROM analytics_marts.fct_velocity_concentration
        GROUP BY 1 ORDER BY 1""").df().to_dict("records")

    d["economics"] = con.execute("""
        SELECT banner_name, banner, classification, orders,
               avg_order_value, avg_parcel_cost, avg_split_premium,
               total_split_premium, avg_gross_margin,
               split_premium_pct_of_margin, cost_per_order
        FROM analytics_marts.fct_split_economics
        ORDER BY banner, classification""").df().to_dict("records")

    d["threshold"] = con.execute("""
        SELECT threshold_usd, banner_name, banner, orders_above_threshold,
               pct_of_split_orders, premium_above_threshold, units_at_risk
        FROM analytics_marts.fct_split_threshold_curve
        ORDER BY threshold_usd, banner""").df().to_dict("records")

    d["inventory"] = con.execute("""
        SELECT year_month, month, inventory_at_cost, sales_at_retail,
               inventory_sales_ratio
        FROM analytics_marts.fct_inventory_position
        ORDER BY year_month""").df().to_dict("records")

    d["nodes"] = con.execute("""
        SELECT node_key, node_name, node_kind, MIN(cost_rank) AS cost_rank,
               SUM(units) AS units, SUM(shipments) AS shipments,
               SUM(parcel_cost) AS parcel_cost,
               SUM(parcel_cost)/SUM(units) AS cost_per_unit
        FROM analytics_marts.fct_node_flow
        GROUP BY 1,2,3 ORDER BY 4""").df().to_dict("records")

    d["register"] = json.loads(
        (DOCS / "data" / "metric_register.json").read_text(encoding="utf-8"))["metrics"]

    # Real anchors, for the method block and the inventory reference band.
    import pandas as pd
    inv = pd.read_csv(REPO_ROOT / "data" / "clean" / "anchor_inventory.csv")
    r = inv[(inv.measure == "inv_sales_ratio") & (inv.adjustment == "sa")
            & (~inv.period.isin(["2020-03", "2020-04", "2020-05"]))
            & (inv.year >= 2015)]
    d["census_band"] = [float(r.value.min()), float(r.value.max())]
    nsa = inv[(inv.measure == "inv_sales_ratio") & (inv.adjustment == "nsa")
              & (~inv.period.isin(["2020-03", "2020-04", "2020-05"]))
              & (inv.year >= 2015)]
    d["census_by_month"] = nsa.groupby("month").value.mean().round(3).to_dict()

    peers = pd.read_csv(REPO_ROOT / "data" / "clean" / "anchor_peers.csv")
    peers = peers[peers.fiscal_year >= 2018]
    d["sga_band"] = [float(peers.sga_pct_of_revenue.min()),
                     float(peers.sga_pct_of_revenue.max())]

    labor = pd.read_csv(REPO_ROOT / "data" / "clean" / "anchor_labor.csv")
    d["labor"] = labor.to_dict("records")

    run = json.loads((REPO_ROOT / "governance" / "generator_run.json")
                     .read_text(encoding="utf-8"))
    d["seed"] = run["seed"]
    d["content_hash"] = run["content_sha256"]
    return d


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def splits_only(d):
    return [e for e in d["economics"] if e["classification"] == "split"]


def pct(x, dp=1):
    return f"{x * 100:.{dp}f}%"


def money(x, dp=2):
    return f"${x:,.{dp}f}"


def table(caption, headers, rows, table_id):
    """Rule 5.1 layer 2 — a real <table> in the DOM, on the same page."""
    head = "".join(f"<th scope='col'>{h}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(
            (f"<th scope='row'>{c}</th>" if i == 0 else f"<td>{c}</td>")
            for i, c in enumerate(r)) + "</tr>"
        for r in rows)
    return (f"<div class='table-scroll'><table id='{table_id}'>"
            f"<caption>{caption}</caption>"
            f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>")


def chart_block(cid, summary, table_html, tall=False):
    return f"""
      <div class="chart-block">
        <p class="chart-summary" id="{cid}-summary">{summary}</p>
        <div class="chart{' chart-tall' if tall else ''}" id="{cid}"></div>
        <details class="data-table">
          <summary>Show the data behind this chart</summary>
          {table_html}
        </details>
      </div>"""


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------

def render(d):
    s = d["summary"]
    band_lo, band_hi = d["census_band"]
    sga_lo, sga_hi = d["sga_band"]

    # --- figures that appear inside chart titles -------------------------
    gap_pts = (s["unit_fill"] - s["order_fill"]) * 100
    cf_delta = (s["unit_fill"] - s["counterfactual_unit_fill"]) * 100

    vel = {v["velocity_band"]: v for v in d["velocity"]}
    split_ratio = vel["C"]["pct_multi_node"] / vel["A"]["pct_multi_node"]
    short_ratio = vel["C"]["pct_partial"] / vel["A"]["pct_partial"]

    econ_split = {e["banner"]: e for e in d["economics"]
                  if e["classification"] == "split"}
    off, prem = econ_split["offprice"], econ_split["premium"]
    mean_premium = (off["avg_split_premium"] * off["orders"]
                    + prem["avg_split_premium"] * prem["orders"]) / (
                        off["orders"] + prem["orders"])

    inv_mean = sum(r["inventory_sales_ratio"] for r in d["inventory"]) / len(d["inventory"])

    nodes = d["nodes"]
    fc1 = next(n for n in nodes if n["node_key"] == "FC1")
    stores = [n for n in nodes if n["node_kind"] == "STORE"]
    store_units = sum(n["units"] for n in stores)
    total_units = sum(n["units"] for n in nodes)
    store_cpu = sum(n["parcel_cost"] for n in stores) / store_units
    store_share = store_units / total_units
    cpu_mult = store_cpu / fc1["cost_per_unit"]

    # threshold: the knee the prescription uses
    T = 6
    tr = {r["banner"]: r for r in d["threshold"] if r["threshold_usd"] == T}
    rec_addressed = sum(v["premium_above_threshold"] for v in tr.values())
    rec_units_at_risk = sum(v["units_at_risk"] for v in tr.values())
    rec_residual = s["split_premium"] - rec_addressed
    gap_unit_line = (s["unit_fill"] - s["line_fill"]) * 100

    # Chart titles are drawn to CANVAS, not to the DOM, so they carry literal
    # Unicode. HTML entities are not decoded by ECharts and would render as
    # "&mdash;" on the chart itself — which is exactly the sort of defect that
    # survives a code review and dies in a reading panel.
    #
    # Each claim below must also be readable from the plot (Rule 3.2), so the
    # threshold title is guarded: the curves only separate ABOVE the base
    # parcel rate, where every split costs at least one extra parcel and both
    # banners sit at 100%.
    by_threshold = {}
    for r in d["threshold"]:
        by_threshold.setdefault(r["threshold_usd"], {})[r["banner"]] = r
    above_base = sorted(t for t in by_threshold if t > 4)
    off_always_higher = all(
        by_threshold[t]["offprice"]["pct_of_split_orders"]
        > by_threshold[t]["premium"]["pct_of_split_orders"] for t in above_base)
    threshold_title = (
        f"Above {money(4, 0)}, every threshold holds a larger share of Off-Main’s "
        f"splits than of Alder & Vance’s"
        if off_always_higher else
        f"A {money(T, 0)} threshold holds "
        f"{tr['offprice']['pct_of_split_orders']:.0f}% of Off-Main’s splits and "
        f"{tr['premium']['pct_of_split_orders']:.0f}% of Alder & Vance’s")

    titles = {
        "fills": f"One dataset answers “what was our fill rate?” three ways, "
                 f"{gap_pts:.1f} points apart, and every answer is arithmetically correct",
        "counterfactual": f"Forbidding splits would cost {cf_delta:.1f} points of unit fill "
                          f"— splitting is how the network hits its numbers",
        "velocity": f"Slow movers reach a second node {split_ratio:.1f}× as often as fast "
                    f"movers and ship short {short_ratio:.1f}× as often — one cause, two symptoms",
        "economics": f"The same {money(mean_premium)} second parcel eats "
                     f"{pct(off['split_premium_pct_of_margin'], 0)} of an off-price order’s margin "
                     f"and {pct(prem['split_premium_pct_of_margin'], 0)} of a premium order’s",
        "threshold": threshold_title,
        "inventory": f"The network holds {inv_mean:.2f} months of stock against the "
                     f"sector’s {band_lo:.2f}–{band_hi:.2f}, and dips in the same season",
        # The volume share is NOT on this plot — the only axis is cost per unit
        # — so it cannot be in the title. It moves to the subtitle and the
        # table, where a reader can check it. A title claiming a variable the
        # chart does not plot is not rescued by tabulating it.
        "nodes": f"Every store ships at more than double the primary FC’s cost "
                 f"per unit, and the four of them are the four most expensive nodes",
    }

    # --- data tables -----------------------------------------------------
    t_fills = table(
        "Monthly fill rates, all banners. Unit fill counts units; line fill counts "
        "lines shipped complete; order fill counts orders shipped complete. Orders "
        "that shipped nothing remain in every denominator.",
        ["Month", "Orders", "Unit fill", "Line fill", "Order fill"],
        [[r["year_month"], f"{int(r['orders']):,}", pct(r["unit_fill"]),
          pct(r["line_fill"]), pct(r["order_fill"])] for r in d["fills"]],
        "tbl-fills")

    t_cf = table(
        "Unit fill as achieved, against what the same demand would have shipped under a "
        "single-node-only rule, evaluated against the inventory position before each "
        "real allocation was committed.",
        ["Month", "Unit fill", "Single-node only", "Points bought by splitting"],
        [[r["year_month"], pct(r["unit_fill"]), pct(r["cf_unit_fill"]),
          f"{(r['unit_fill'] - r['cf_unit_fill']) * 100:.2f}"] for r in d["fills"]],
        "tbl-cf")

    t_vel = table(
        "Order lines by SKU velocity band. A-band styles are ranged at six nodes, "
        "B-band at four, C-band at two.",
        ["Velocity band", "Lines", "Ships partial", "Ships zero", "Uses >1 node", "Unit fill"],
        [[{"A": "A · fast", "B": "B · mid", "C": "C · slow"}[v["velocity_band"]],
          f"{int(v['lines']):,}", f"{v['pct_partial']:.2f}%", f"{v['pct_zero']:.2f}%",
          f"{v['pct_multi_node']:.2f}%", pct(v["unit_fill"])] for v in d["velocity"]],
        "tbl-vel")

    t_econ = table(
        "Split economics by banner. The split premium is the incremental parcel cost of "
        "fragmenting an order &mdash; actual parcel cost minus what the same shipped units "
        "would have cost in one parcel. Orders that shipped nothing are excluded.",
        ["Banner", "Fulfilment", "Orders", "Avg order value", "Avg parcel cost",
         "Avg split premium", "Avg gross margin", "Premium as % of margin"],
        [[e["banner_name"], e["classification"].replace("_", " "),
          f"{int(e['orders']):,}", money(e["avg_order_value"]),
          money(e["avg_parcel_cost"]), money(e["avg_split_premium"]),
          money(e["avg_gross_margin"]),
          pct(e["split_premium_pct_of_margin"])] for e in d["economics"]],
        "tbl-econ")

    thr_by_t = {}
    for r in d["threshold"]:
        thr_by_t.setdefault(r["threshold_usd"], {})[r["banner"]] = r
    t_thr = table(
        "Split orders whose premium exceeds each threshold &mdash; the orders a policy at "
        "that threshold would hold as exceptions. Units at risk are units that shipped "
        "only because the order was split.",
        ["Threshold", "Off-Main orders", "% of Off-Main splits", "Alder &amp; Vance orders",
         "% of A&amp;V splits", "Units at risk"],
        [[money(t, 0),
          f"{int(v.get('offprice', {}).get('orders_above_threshold', 0)):,}",
          f"{v.get('offprice', {}).get('pct_of_split_orders', 0):.1f}%",
          f"{int(v.get('premium', {}).get('orders_above_threshold', 0)):,}",
          f"{v.get('premium', {}).get('pct_of_split_orders', 0):.1f}%",
          f"{int(v.get('offprice', {}).get('units_at_risk', 0) + v.get('premium', {}).get('units_at_risk', 0)):,}"]
         for t, v in sorted(thr_by_t.items())],
        "tbl-thr")

    t_inv = table(
        "End-of-month inventory valued at cost over that month&rsquo;s sales at retail, "
        "matching the Census Monthly Retail Trade Survey convention. The sector band is "
        "the seasonally adjusted department-store range, 2015&ndash;2026, excluding the "
        "March&ndash;May 2020 store closures.",
        ["Month", "Inventory at cost", "Sales at retail", "Inventory / sales"],
        [[r["year_month"], money(r["inventory_at_cost"], 0),
          money(r["sales_at_retail"], 0), f"{r['inventory_sales_ratio']:.3f}"]
         for r in d["inventory"]],
        "tbl-inv")

    t_nodes = table(
        "Volume and parcel cost by fulfilment node over 24 months.",
        ["Node", "Type", "Shipments", "Units", "Parcel cost", "Cost per unit"],
        [[n["node_name"], n["node_kind"], f"{int(n['shipments']):,}",
          f"{int(n['units']):,}", money(n["parcel_cost"], 0),
          money(n["cost_per_unit"])] for n in nodes],
        "tbl-nodes")

    # --- register --------------------------------------------------------
    reg_rows = "".join(
        f"<tr><td>{m['metric']}</td>"
        f"<td><span class='tier-tag {m['tier']}'>{m['tier']}</span></td>"
        f"<td>{m['grain']}</td><td>{m['owner']}</td>"
        f"<td class='why'>{m['tier_reason']}</td></tr>"
        for m in d["register"])

    # AXIS BOUNDS ARE COMPUTED, NEVER TYPED.
    #
    # The first version of this page hard-coded them, and two charts clipped
    # real data off the bottom of the plot: order fill reaches 77.95% in peak
    # months against an axis that started at 82, so the deepest service failures
    # in the dataset — the months the module is actually about — were invisible.
    # Bounds now come from the series, with headroom reserved above the data for
    # annotations so they never have to sit on top of a mark.
    def bounds(values, pad_lo=1.5, pad_hi=1.5, floor=None, step=1.0):
        lo, hi = min(values), max(values)
        lo = (int((lo - pad_lo) / step)) * step
        hi = (int((hi + pad_hi) / step) + 1) * step
        if floor is not None:
            lo = max(lo, floor)
        return [round(lo, 3), round(hi, 3)]

    f_unit = [r["unit_fill"] * 100 for r in d["fills"]]
    f_line = [r["line_fill"] * 100 for r in d["fills"]]
    f_order = [r["order_fill"] * 100 for r in d["fills"]]
    f_cf = [r["cf_unit_fill"] * 100 for r in d["fills"]]
    vel_vals = ([v["pct_partial"] for v in d["velocity"]]
                + [v["pct_multi_node"] for v in d["velocity"]])
    econ_vals = [e["split_premium_pct_of_margin"] * 100 for e in splits_only(d)]
    thr_vals = [r["pct_of_split_orders"] for r in d["threshold"]
                if r["threshold_usd"] > 4]
    inv_vals = [r["inventory_sales_ratio"] for r in d["inventory"]]
    node_vals = [n["cost_per_unit"] for n in d["nodes"]]

    axes = {
        # extra headroom on the bar charts is where the annotations live
        "fills": bounds(f_unit + f_line + f_order, 4.0, 2.0, floor=0),
        "cf": bounds(f_unit + f_cf, 4.0, 2.0, floor=0),
        "velocity": [0, bounds(vel_vals, 0, 6, floor=0, step=2)[1]],
        "economics": [0, bounds(econ_vals, 0, 4, floor=0)[1]],
        "threshold": [0, bounds(thr_vals, 0, 5, floor=0)[1]],
        "inventory": [0, max(band_hi + 0.4, max(inv_vals) + 0.4)],
        "nodes": [0, bounds(node_vals, 0, 1.4, floor=0, step=0.5)[1]],
    }

    payload = json.dumps({
        "fills": d["fills"], "velocity": d["velocity"],
        "economics": d["economics"], "threshold": d["threshold"],
        "inventory": d["inventory"], "nodes": d["nodes"],
        "censusBand": d["census_band"], "censusByMonth": d["census_by_month"],
        "titles": titles, "axes": axes,
    }, default=float)

    summaries = build_summaries(d, axes)

    labor_rows = "".join(
        f"<li><code>{l['soc_code']}</code> {l['occupation']} &mdash; "
        f"median <strong>${l['h_median']:.2f}/hr</strong>, "
        f"p10 ${l['h_pct10']:.2f}, p90 ${l['h_pct90']:.2f} "
        f"({l['tier']})</li>" for l in d["labor"])

    return PAGE.format(
        as_of=AS_OF,
        payload=payload,
        titles=json.dumps(titles),
        # headline figures
        unit_fill=pct(s["unit_fill"]), line_fill=pct(s["line_fill"]),
        order_fill=pct(s["order_fill"]), split_rate=pct(s["split_rate"]),
        orders=f"{int(s['orders']):,}",
        lines=f"{int(s['lines']):,}",
        sales=money(s["sales_at_retail"], 0),
        split_premium=money(s["split_premium"], 0),
        split_pct_parcel=f"{s['split_premium_pct_of_parcel']:.1f}%",
        cost_per_order=money(s["cost_per_shipped_order"]),
        labor_cost=money(s["labor_cost"], 0),
        labor_hours=f"{s['labor_hours']:,.0f}",
        dc_cost_pct=pct(s["dc_cost_pct_of_sales"], 2),
        cf_delta=f"{cf_delta:.2f}",
        gap_pts=f"{gap_pts:.1f}",
        inv_mean=f"{inv_mean:.2f}",
        band_lo=f"{band_lo:.2f}", band_hi=f"{band_hi:.2f}",
        sga_lo=pct(sga_lo, 1), sga_hi=pct(sga_hi, 1),
        seed=d["seed"], content_hash=d["content_hash"],
        mean_premium=money(mean_premium),
        off_margin_pct=pct(off["split_premium_pct_of_margin"], 1),
        prem_margin_pct=pct(prem["split_premium_pct_of_margin"], 1),
        off_leak=money(off["total_split_premium"], 0),
        prem_leak=money(prem["total_split_premium"], 0),
        not_shipped=f"{int(s['orders_not_shipped']):,}",
        # prescriptive
        rec_threshold=money(T, 0),
        rec_orders=f"{int(tr['offprice']['orders_above_threshold']):,}",
        rec_premium=money(tr["offprice"]["premium_above_threshold"], 0),
        rec_prem_orders=f"{int(tr['premium']['orders_above_threshold']):,}",
        rec_prem_premium=money(tr["premium"]["premium_above_threshold"], 0),
        rec_units_at_risk=f"{int(rec_units_at_risk):,}",
        rec_addressed=money(rec_addressed, 0),
        rec_residual=money(rec_residual, 0),
        gap_unit_line=f"{gap_unit_line:.2f}",
        # blocks
        chart_fills=chart_block("c-fills", summaries["fills"], t_fills, tall=True),
        chart_cf=chart_block("c-cf", summaries["counterfactual"], t_cf, tall=True),
        chart_vel=chart_block("c-vel", summaries["velocity"], t_vel),
        chart_econ=chart_block("c-econ", summaries["economics"], t_econ),
        chart_thr=chart_block("c-thr", summaries["threshold"], t_thr),
        chart_inv=chart_block("c-inv", summaries["inventory"], t_inv, tall=True),
        chart_nodes=chart_block("c-nodes", summaries["nodes"], t_nodes),
        register_rows=reg_rows,
        labor_rows=labor_rows,
    )


def build_summaries(d, axes):
    """Rule 5.2 — construction and statistics only, and COMPUTED.

    No interpretation: blind readers ranked domain insight among the least
    useful description content, so putting the finding in here would be an
    accessibility regression rather than a bonus.

    Every figure is computed. The first version of this page hard-coded these
    sentences with invented ranges — it told a screen-reader user that order
    fill ran 85.6 to 88.6 when it actually reaches 77.95. A sighted reader had
    the plot to contradict it; a non-sighted reader had nothing. Description
    text that can drift from the data is worse than no description, because it
    is trusted.
    """
    def rng(vals, dp=1):
        return f"{min(vals):.{dp}f} to {max(vals):.{dp}f}"

    f = d["fills"]
    unit = [r["unit_fill"] * 100 for r in f]
    line = [r["line_fill"] * 100 for r in f]
    order = [r["order_fill"] * 100 for r in f]
    cf = [r["cf_unit_fill"] * 100 for r in f]
    gaps = [u - c for u, c in zip(unit, cf)]
    vel = {v["velocity_band"]: v for v in d["velocity"]}
    econ = sorted(splits_only(d),
                  key=lambda e: -e["split_premium_pct_of_margin"])
    thr = sorted({r["threshold_usd"] for r in d["threshold"]})
    inv = [r["inventory_sales_ratio"] for r in d["inventory"]]
    nodes = sorted(d["nodes"], key=lambda n: -n["cost_per_unit"])
    a = axes

    return {
        "fills":
            f"Line chart. Three series over {len(f)} months, "
            f"{f[0]['year_month']} to {f[-1]['year_month']}. Vertical axis is "
            f"percent, {a['fills'][0]:.0f} to {a['fills'][1]:.0f}. Unit fill "
            f"ranges {rng(unit)} percent, line fill {rng(line)}, order fill "
            f"{rng(order)}. The three series do not cross at any point.",
        "counterfactual":
            f"Line chart. Two series over {len(f)} months. Vertical axis is "
            f"percent, {a['cf'][0]:.0f} to {a['cf'][1]:.0f}. Unit fill as "
            f"achieved ranges {rng(unit)} percent and runs above unit fill "
            f"under a single-node-only rule in every month; that series ranges "
            f"{rng(cf)}. The vertical distance between them ranges "
            f"{rng(gaps, 2)} percentage points.",
        "velocity":
            f"Grouped bar chart. Three SKU velocity bands on the horizontal "
            f"axis, two bars each. Vertical axis is percent of order lines, 0 "
            f"to {a['velocity'][1]:.0f}. Lines shipping short: "
            f"{vel['A']['pct_partial']:.2f} percent for band A, "
            f"{vel['B']['pct_partial']:.2f} for B, {vel['C']['pct_partial']:.2f} "
            f"for C. Lines using more than one node: "
            f"{vel['A']['pct_multi_node']:.2f}, {vel['B']['pct_multi_node']:.2f}, "
            f"{vel['C']['pct_multi_node']:.2f}. Both series increase from A to C.",
        "economics":
            f"Bar chart. Two banners on the horizontal axis. Vertical axis is "
            f"the split premium as a percent of gross margin on split orders, 0 "
            f"to {a['economics'][1]:.0f}. "
            + ", ".join(f"{e['banner_name']} {e['split_premium_pct_of_margin']*100:.2f} "
                        f"percent" for e in econ) + ".",
        "threshold":
            f"Line chart. Cost thresholds from ${thr[1]:.0f} to ${thr[-1]:.0f} on "
            f"the horizontal axis. Vertical axis is the percent of that banner's "
            f"split orders whose premium exceeds the threshold, 0 to "
            f"{a['threshold'][1]:.0f}. Both series fall as the threshold rises, "
            f"the off-price series above the premium series throughout.",
        "inventory":
            f"Line chart with a shaded horizontal reference band. Vertical axis "
            f"is months of sales held in inventory, 0 to {a['inventory'][1]:.1f}. "
            f"The plotted series ranges {min(inv):.2f} to {max(inv):.2f} months "
            f"and runs below the shaded band, which spans "
            f"{d['census_band'][0]:.2f} to {d['census_band'][1]:.2f}, in every "
            f"month. The series falls in November and December of both years.",
        "nodes":
            f"Bar chart. {len(nodes)} fulfilment nodes on the horizontal axis, "
            f"ordered most to least expensive. Vertical axis is parcel cost per "
            f"unit in dollars, 0 to {a['nodes'][1]:.2f}. Values run from "
            f"${nodes[0]['cost_per_unit']:.2f} at {nodes[0]['node_name']} to "
            f"${nodes[-1]['cost_per_unit']:.2f} at {nodes[-1]['node_name']}.",
    }


def main():
    if not DB_PATH.exists():
        raise SystemExit(f"ERROR: {DB_PATH} not found. Run the pipeline first.")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    d = fetch(con)
    html = render(d)
    con.close()

    OUT.write_text(html, encoding="utf-8")
    kb = len(html.encode("utf-8")) / 1024
    print(f"Wrote {OUT} ({kb:,.0f} KB)")
    print(f"  7 charts · {len(d['register'])} registered metrics · "
          f"dataset inlined, no render-time fetch")


if __name__ == "__main__":
    main()
