"""
generate.py — the seeded generator for Alder & Vance Retail Group.

Cascadia Control Tower · synthetic operational spine

Output: data/clean/controltower.duckdb   (star schema)
        governance/generator_run.json    (realized mix vs target, content hash)

READ THIS FILE TOP TO BOTTOM. The code is part of the argument.

WHAT THIS BUILDS
----------------
Twenty-four months of fulfillment activity for an invented two-banner
department-store operation: a premium banner (Alder & Vance) and an off-price
banner (Off-Main), sharing one primary distribution centre inside a six-node
network that also ships from a second FC and four stores.

WHAT MUST BE EMERGENT, NOT PAINTED ON
-------------------------------------
Three behaviours carry the module's argument. If any of them were hard-coded the
module would be a slideshow, so each falls out of the simulation instead:

1. **Splits.** No order is ever labelled "split". An order splits when the
   allocator cannot satisfy every line from one node and has to reach for a
   second. That happens where inventory is fragmented relative to what customers
   actually put in a basket — slow-moving SKUs stocked in one place, fast movers
   stocked out at the cheap node. Cause, not noise.

2. **Fill-rate divergence.** Order fill, line fill and unit fill are never
   assigned. They are three different arithmetics over the same shipped
   quantities, computed at the end, and they disagree because they are
   genuinely different questions.

3. **Different split economics by banner.** Never coded as a rule. It falls out
   of unit value: the same ~$6 second parcel is a rounding error against a
   premium order's margin and a catastrophe against an off-price order's.

THE THING THE MODULE IS ABOUT
-----------------------------
Splitting is *how the network achieves fill*. The allocator splits to rescue
orders it would otherwise short. So the segments that split most also post the
best fill rates — while costing the most to serve. To make that provable rather
than assertable, the simulation also records, for every order, what would have
happened under a single-node-only rule. That counterfactual is what prices the
governance decision.

DETERMINISM
-----------
One `random.Random(SEED)`, drawn from in a fixed order, iterating sorted
collections only. Same seed produces the same content hash, recorded in
governance/generator_run.json. The hash is over table CONTENT (sorted rows), not
over the DuckDB file, because storage-engine internals are not the claim being
made — the data is.

Usage:
    python src/generate.py
"""

import hashlib
import json
import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import duckdb
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
CLEAN_DIR = REPO_ROOT / "data" / "clean"
GOV_DIR = REPO_ROOT / "governance"
DB_PATH = CLEAN_DIR / "controltower.duckdb"

SEED = 20260808

# ===========================================================================
# 1 · PARAMETERS
#
# Every tunable lives here, and every one of them is reproduced with its
# rationale in governance/generator_assumptions.md. Nothing that shapes the
# world is buried further down.
# ===========================================================================

PARAMS = {
    "period_start": date(2024, 8, 1),
    "period_end": date(2026, 7, 31),

    # Order volume. A mid-size fulfillment node: large enough that a fractional
    # split rate is real money, small enough to be honest about a single DC that
    # still ships a lot of its demand from stores.
    "base_orders_per_day": 500,
    "weekday_multiplier": {0: 1.12, 1: 1.06, 2: 1.02, 3: 1.00,
                           4: 0.98, 5: 0.86, 6: 0.96},
    "month_multiplier": {1: 0.88, 2: 0.82, 3: 0.90, 4: 0.92, 5: 0.96,
                         6: 0.94, 7: 0.98, 8: 0.95, 9: 0.97, 10: 1.06,
                         11: 1.62, 12: 1.48},

    # Assortment.
    "styles_per_banner": 1200,
    "velocity_mix": {"A": 0.20, "B": 0.30, "C": 0.50},      # share of SKUs
    "velocity_demand_share": {"A": 0.70, "B": 0.22, "C": 0.08},

    # Banner economics. The premium/off-price gap is the whole second finding,
    # so it is set once, here, and never referenced as a special case later.
    "banner": {
        "premium": {"name": "Alder & Vance", "order_share": 0.42,
                    "unit_value_mean": 88.0, "unit_value_sd": 34.0,
                    "gross_margin": 0.385, "lines_lambda": 0.88,
                    "cover_weeks": 1.86},
        "offprice": {"name": "Off-Main", "order_share": 0.58,
                     "unit_value_mean": 26.0, "unit_value_sd": 9.5,
                     "gross_margin": 0.302, "lines_lambda": 1.19,
                     "cover_weeks": 1.38},
    },

    # Where each velocity band is stocked. This single table is what makes
    # splits concentrate on a cause rather than scatter: a slow mover lives in
    # very few places, so any basket mixing it with a stocked-out fast mover
    # must reach for a second node.
    #
    # C-band is TWO nodes, not one, and the difference matters. At one node a
    # slow mover can only ever be short — there is no second node to rescue it
    # from — so the segment with the thinnest stock would short constantly and
    # split never, which is the exact opposite of the behaviour under study. At
    # two nodes the same thin stock produces both outcomes from one cause, and
    # the co-occurrence the module is about becomes observable instead of
    # asserted.
    "stocking_breadth": {"A": 6, "B": 4, "C": 2},

    # Replenishment. Off-price runs leaner cover, which is why it stocks out
    # more, which is why it splits more. Consequence, not a coded rule.
    "review_period_days": 7,
    "lead_time_days": {"FC1": 5, "FC2": 6, "STORE": 3},
    "safety_stock_weeks": {"A": 0.55, "B": 0.40, "C": 0.30},

    # Cover held per node, as a multiple of the banner's cover. This is the
    # single most consequential line in the file, and it is a real operating
    # asymmetry rather than a dial: the primary FC is run lean because it turns
    # fastest, while stores hold SELLING inventory sized for footfall, not for
    # fulfillment. So the store frequently has a unit on the day the FC does
    # not — which is precisely the condition that produces a split rather than
    # a shortfall. Remove this asymmetry and splits collapse toward zero.
    "node_cover_multiplier": {"FC1": 0.86, "FC2": 1.00, "STORE": 1.18},

    # Weekly demand volatility per SKU. Replenishment targets are set once from
    # AVERAGE demand, so a SKU that runs hot for a week outruns its plan and
    # the whole network goes short together. This is the lever that produces
    # shortfall, and it is deliberately separate from the node asymmetry above,
    # which produces splits. Without two independent levers, any attempt to
    # lower fill also raises the split rate and the two cannot be set to
    # realistic values at the same time.
    "weekly_shock_sigma": 0.45,

    # Inventory record accuracy. A pick shorts when the system says five and
    # the bin holds three. This is the most ordinary failure in a DC and it is
    # the only mechanism that produces PARTIALLY filled lines at scale — which
    # is what separates unit fill from line fill. Without it those two metrics
    # are the same number wearing different names, and the module's headline
    # claim of three genuinely different answers would not survive inspection.
    # Phantom units are written off as an inventory adjustment, so the ledger
    # still balances.
    "phantom_pick_rate": 0.07,

    # Store fulfillment buffer. A store's stock is SELLING stock; it is not all
    # available to ship. Retailers hold a buffer back so fulfillment does not
    # strip the floor, and expose only a fraction of the rest.
    #
    # This is what makes partially filled lines common, and partially filled
    # lines are the only thing that separates unit fill from line fill: a line
    # that ships four of six units counts as a failure to line fill but as
    # two-thirds of a success to unit fill. With stores exposing everything,
    # a large line either ships whole or not at all, and the two metrics
    # collapse onto the same number.
    "store_fulfillment_buffer": 2,
    "store_atp_fraction": 0.45,

    # Units per line. Kept above one on purpose: if every line were a single
    # unit, line fill and unit fill would be the same number by construction
    # and the module's central claim would be untestable.
    "qty_mean_excess": 2.4,
    "qty_cap": 8,

    # Cost model. Parcel economics are the leak; labor is the denominator that
    # makes units-per-hour meaningful.
    "parcel_base_cost": 4.35,          # per parcel, any node
    "parcel_cost_per_unit": 0.62,
    "store_pick_penalty": 1.85,        # stores are worse at this than an FC
    "units_per_labor_hour": {"receiving": 142, "putaway": 96,
                             "picking": 68, "packing": 54, "shipping": 128},

    # Service promise.
    "promise_days": {"premium": 3, "offprice": 5},

    # Inventory hygiene.
    "monthly_shrink_rate": 0.0011,

    # Calibration targets, reported against in generator_assumptions.md. These
    # are aims, not assignments — nothing downstream forces them, and the run
    # reports the realized figure whether or not it lands.
    #
    # The three fill rates are targeted because they are the module's stated
    # thesis: a DC reporting 94% to Operations, 91% to the merchant team and
    # 87% to Finance. Split rate carries NO target on purpose. It is a free
    # outcome of inventory position and the allocation rule, and inventing a
    # target for it and then tuning until it was hit would be circular — the
    # split rate would then be evidence of nothing except that it had been
    # dialled in. Realism audit C checks that splitting is concentrated and
    # directional, which is a claim about structure rather than level.
    "targets": {"unit_fill": 0.94, "line_fill": 0.91, "order_fill": 0.87},
}

VELOCITY_BANDS = ["A", "B", "C"]

# Categories and their size runs.
#
# THIS IS WHY THE THREE FILL RATES DIVERGE. Stock is held per style AND size, so
# a line for three units of one style is three units of one SIZE, drawn against
# a bin that typically holds a handful. The line ships two of three far more
# often than it ships three or nothing.
#
# That matters because unit fill only separates from line fill through partially
# filled lines: two of three units is a total failure to line fill but two
# thirds of a success to unit fill. Holding inventory at style level — which is
# what the first version of this generator did — makes lines behave as
# all-or-nothing, and unit fill and line fill collapse onto the same number.
#
# Size brokenness is also simply the truth about retail. It is the single
# commonest reason a retail order line ships incomplete, and a fulfillment model
# without it is missing the main event.
CATEGORY_CONFIG = {
    "Apparel":     {"weight": 0.40, "sizes": ["XS", "S", "M", "L", "XL"],
                    "shares": [0.10, 0.22, 0.30, 0.24, 0.14]},
    "Footwear":    {"weight": 0.20, "sizes": ["6", "7", "8", "9", "10", "11"],
                    "shares": [0.08, 0.15, 0.22, 0.24, 0.19, 0.12]},
    "Accessories": {"weight": 0.15, "sizes": ["OS"], "shares": [1.0]},
    "Home":        {"weight": 0.15, "sizes": ["OS"], "shares": [1.0]},
    "Beauty":      {"weight": 0.10, "sizes": ["OS"], "shares": [1.0]},
}
CATEGORIES = list(CATEGORY_CONFIG)

NODES = [
    # code, label, kind, cost rank (lower is cheaper to serve from)
    ("FC1", "Cascade Ridge FC", "FC", 1),
    ("FC2", "Fernhill FC", "FC", 2),
    ("S01", "Store 101", "STORE", 3),
    ("S02", "Store 102", "STORE", 4),
    ("S03", "Store 103", "STORE", 5),
    ("S04", "Store 104", "STORE", 6),
]
NODE_ORDER = [n[0] for n in NODES]          # cheapest-first, deterministic


# ===========================================================================
# 2 · DIMENSIONS
# ===========================================================================

def build_dimensions(rng: random.Random):
    days = []
    d = PARAMS["period_start"]
    while d <= PARAMS["period_end"]:
        days.append({
            "date_key": int(d.strftime("%Y%m%d")), "full_date": d,
            "year": d.year, "month": d.month, "day": d.day,
            "weekday": d.weekday(),
            "year_month": f"{d.year}-{d.month:02d}",
            "is_weekend": d.weekday() >= 5,
            "is_peak_season": d.month in (11, 12),
        })
        d += timedelta(days=1)

    # Categories are assigned by cumulative weight across the style index rather
    # than drawn at random, so the assortment mix is exact rather than
    # approximately right.
    cat_cum, run = [], 0.0
    for c in CATEGORIES:
        run += CATEGORY_CONFIG[c]["weight"]
        cat_cum.append((run, c))

    def category_for(idx: int, n: int) -> str:
        pos = (idx + 0.5) / n
        for edge, c in cat_cum:
            if pos <= edge:
                return c
        return CATEGORIES[-1]

    styles, skus = [], []
    for banner in ("premium", "offprice"):
        cfg = PARAMS["banner"][banner]
        n = PARAMS["styles_per_banner"]
        counts = {b: int(n * PARAMS["velocity_mix"][b]) for b in VELOCITY_BANDS}
        counts["C"] += n - sum(counts.values())          # absorb rounding
        i = 0
        for band in VELOCITY_BANDS:
            for j in range(counts[band]):
                value = max(3.0, rng.gauss(cfg["unit_value_mean"],
                                           cfg["unit_value_sd"]))
                # Slow movers skew expensive — that is why they are slow, and it
                # is what makes a C-band line worth rescuing with a second
                # parcel even when the arithmetic says otherwise.
                if band == "B":
                    value *= 1.12
                elif band == "C":
                    value *= 1.34
                # Category is drawn from the position WITHIN the velocity band,
                # not the position across the whole assortment. Using the global
                # index made the bands come out sorted by category — fast movers
                # were all apparel and slow movers all one-size goods — which
                # would have confounded velocity with sizing and handed the
                # module a finding that was really an artefact of style
                # numbering.
                category = category_for(j, counts[band])
                i += 1
                style_key = f"{'AV' if banner == 'premium' else 'OM'}-{i:05d}"
                styles.append({
                    "style_key": style_key, "banner": banner,
                    "category": category, "velocity_band": band,
                    "unit_value": round(value, 2),
                })
                sizes = CATEGORY_CONFIG[category]["sizes"]
                shares = CATEGORY_CONFIG[category]["shares"]
                for size, share in zip(sizes, shares):
                    skus.append({
                        "sku_key": f"{style_key}-{size}",
                        "style_key": style_key,
                        "size": size,
                        "size_share": share,
                        "banner": banner,
                        "banner_name": cfg["name"],
                        "category": category,
                        "velocity_band": band,
                        "unit_value": round(value, 2),
                        "unit_cost": round(value * (1 - cfg["gross_margin"]), 2),
                        "stocking_breadth": PARAMS["stocking_breadth"][band],
                    })

    for s in styles:
        cfg = PARAMS["banner"][s["banner"]]
        s["banner_name"] = cfg["name"]
        s["unit_cost"] = round(s["unit_value"] * (1 - cfg["gross_margin"]), 2)
        s["size_count"] = len(CATEGORY_CONFIG[s["category"]]["sizes"])
        s["stocking_breadth"] = PARAMS["stocking_breadth"][s["velocity_band"]]

    nodes = [{"node_key": c, "node_name": nm, "node_kind": k, "cost_rank": r}
             for c, nm, k, r in NODES]
    banners = [{"banner_key": b, "banner_name": PARAMS["banner"][b]["name"],
                "positioning": ("Premium" if b == "premium" else "Off-price"),
                "gross_margin": PARAMS["banner"][b]["gross_margin"],
                "promise_days": PARAMS["promise_days"][b]}
               for b in ("premium", "offprice")]
    return days, styles, skus, nodes, banners


def assign_stocking(skus):
    """Which nodes carry each SKU.

    The primary FC carries everything. Beyond that, breadth is filled by taking
    the second FC first and then a SKU-specific subset of stores — not always
    the same stores. Always slicing the cost-ranked list would leave the
    lowest-ranked stores holding only the fastest movers, which would make
    them dead weight in the network and would understate how often a store is
    the only place a unit exists.

    Breadth is decided per STYLE, not per size: a node either ranges a style or
    it does not, and if it ranges it, it ranges the size run. Deciding this per
    size would let a node hold a large and not a medium of the same style, which
    is not how anyone buys or allocates.

    Uses its own generator so that changing anything upstream in the draw order
    cannot silently reshuffle the assortment map.
    """
    r = random.Random(SEED + 1)
    stores = [n for n in NODE_ORDER if n.startswith("S")]
    by_style = {}
    for s in sorted(skus, key=lambda x: x["sku_key"]):
        style = s["style_key"]
        if style not in by_style:
            breadth = s["stocking_breadth"]
            nodes = ["FC1"]
            if breadth >= 2:
                nodes.append("FC2")
            n_stores = max(0, breadth - 2)
            if n_stores:
                nodes.extend(sorted(r.sample(stores,
                                             min(n_stores, len(stores)))))
            by_style[style] = [n for n in NODE_ORDER if n in set(nodes)]
    return {s["sku_key"]: by_style[s["style_key"]] for s in skus}


# ===========================================================================
# 3 · DEMAND
#
# Demand is built per SKU per day so that inventory planning and order
# generation see the same world. Popularity within a velocity band is drawn
# once and held, so a fast mover is fast all year rather than fast on average.
# ===========================================================================

def build_demand_weights(skus, rng):
    """Demand weight per SKU = style popularity x that size's share of the run.

    Popularity is drawn at STYLE level. Customers want a style and then need
    their size; they do not independently prefer a medium of one style and a
    large of another. Drawing at size level would smear the long tail across
    the size run and quietly remove the thin-bin problem this model exists to
    represent.
    """
    style_rows = {}
    for s in skus:
        style_rows.setdefault(s["style_key"], s)

    style_weight = {}
    for banner in ("premium", "offprice"):
        band_styles = defaultdict(list)
        for key, s in style_rows.items():
            if s["banner"] == banner:
                band_styles[s["velocity_band"]].append(key)
        for band in VELOCITY_BANDS:
            keys = sorted(band_styles[band])
            # Long tail within the band: a few styles carry most of the band.
            raw = [rng.paretovariate(1.6) for _ in keys]
            total = sum(raw)
            share = PARAMS["velocity_demand_share"][band]
            for k, r in zip(keys, raw):
                style_weight[k] = share * r / total

    return {s["sku_key"]: style_weight[s["style_key"]] * s["size_share"]
            for s in skus}


def day_order_count(d: date, rng: random.Random) -> int:
    base = PARAMS["base_orders_per_day"]
    m = (PARAMS["weekday_multiplier"][d.weekday()]
         * PARAMS["month_multiplier"][d.month])
    return max(0, int(rng.gauss(base * m, base * m * 0.07)))


# ===========================================================================
# 4 · THE ALLOCATOR — the documented rule that decides splits
#
# This is the rule `governance/classification_rules.md` describes and
# `validate.py` re-derives independently. It is deliberately simple enough to
# state in two sentences to a merchant:
#
#   1. If one node can ship the whole order, use the cheapest such node.
#   2. Otherwise fill line by line, most valuable line first, from the cheapest
#      node that has stock. Anything nobody has is short-shipped.
#
# Nothing in here knows what a "split" is. A split is the observed consequence
# of rule 2 reaching for more than one node.
# ===========================================================================

def allocate(lines, on_hand, eligible, phantom=None):
    """Return {line_index: [(node, qty), ...]} plus the shortfall in units.

    `on_hand` is the live inventory dict and is NOT mutated here — the caller
    commits the allocation, so the counterfactual can be evaluated against the
    same starting position.

    `phantom` is {(sku, node): units} that the record claims exist but the bin
    does not hold. The allocator cannot see the discrepancy in advance, which
    is the whole point: it plans against the record and discovers the truth at
    the pick face.
    """
    phantom = phantom or {}

    def usable(sku, node):
        held = on_hand.get((sku, node), 0) - phantom.get((sku, node), 0)
        if node.startswith("S"):
            # Available to promise, not on hand. The floor keeps the rest.
            held = int((held - PARAMS["store_fulfillment_buffer"])
                       * PARAMS["store_atp_fraction"])
        return max(0, held)

    # Rule 1 — whole order from one node.
    for node in NODE_ORDER:
        if all(node in eligible[ln["sku_key"]]
               and usable(ln["sku_key"], node) >= ln["qty_ordered"]
               for ln in lines):
            return {i: [(node, ln["qty_ordered"])]
                    for i, ln in enumerate(lines)}, 0

    # Rule 2 — line by line, most valuable first, cheapest node with stock.
    taken = defaultdict(int)
    plan = {i: [] for i in range(len(lines))}
    order_by_value = sorted(
        range(len(lines)),
        key=lambda i: (-lines[i]["qty_ordered"] * lines[i]["unit_value"],
                       lines[i]["sku_key"]))
    short_units = 0
    for i in order_by_value:
        ln = lines[i]
        remaining = ln["qty_ordered"]
        for node in NODE_ORDER:
            if remaining <= 0:
                break
            if node not in eligible[ln["sku_key"]]:
                continue
            key = (ln["sku_key"], node)
            avail = usable(*key) - taken[key]
            if avail <= 0:
                continue
            take = min(avail, remaining)
            plan[i].append((node, take))
            taken[key] += take
            remaining -= take
        short_units += remaining
    return plan, short_units


def build_pick_tables(rng, sku_by_key, weights, sigma):
    """Rebuild the weighted-draw tables with this week's demand shocks.

    Each SKU gets a lognormal multiplier with mean 1, so the assortment's total
    demand is unchanged but WHICH SKUs are hot moves week to week. Replenishment
    plans against the long-run average and cannot see this, which is what makes
    a shortfall a genuine planning failure rather than a dice roll.
    """
    tables = {}
    for banner in ("premium", "offprice"):
        keys = sorted(k for k, s in sku_by_key.items() if s["banner"] == banner)
        cum, total = [], 0.0
        for k in keys:
            shock = rng.lognormvariate(-(sigma ** 2) / 2, sigma)
            total += weights[k] * shock
            cum.append(total)
        tables[banner] = (keys, cum, total)
    return tables


def counterfactual_single_node(lines, on_hand, eligible):
    """What the SAME order would have achieved if splitting were forbidden.

    This is what prices the governance decision. Without it, "splitting is how
    the network achieves fill" is an assertion; with it, it is a number.
    """
    best_units = 0
    for node in NODE_ORDER:
        units = 0
        for ln in lines:
            if node not in eligible[ln["sku_key"]]:
                continue
            held = on_hand.get((ln["sku_key"], node), 0)
            if node.startswith("S"):
                # Same available-to-promise rule the real allocator obeys —
                # a counterfactual that quietly relaxed it would overstate
                # what a single node could have done and understate the value
                # of splitting.
                held = int((held - PARAMS["store_fulfillment_buffer"])
                           * PARAMS["store_atp_fraction"])
            units += min(max(0, held), ln["qty_ordered"])
        best_units = max(best_units, units)
    return best_units


# ===========================================================================
# 5 · THE SIMULATION
# ===========================================================================

def simulate(rng: random.Random, days, styles, skus, placement, weights):
    sku_by_key = {s["sku_key"]: s for s in skus}
    sku_keys = sorted(sku_by_key)

    # Size run per style, with each size's share of demand. An order LINE is a
    # style and a quantity; the sizes are what the customer actually needs and
    # what the warehouse must actually find.
    sizes_by_style = defaultdict(list)
    for s in sorted(skus, key=lambda x: x["sku_key"]):
        sizes_by_style[s["style_key"]].append((s["sku_key"], s["size_share"]))
    style_of_sku = {s["sku_key"]: s["style_key"] for s in skus}

    # --- opening inventory and replenishment plan ---------------------------
    # Weekly demand per SKU per node, used for cover-based stocking. A node's
    # share of a SKU's demand is proportional to how few nodes carry it.
    # Expected units per SKU per day, used to size stock. The estimate is built
    # from the same distributions the order loop draws from — mean lines per
    # order and mean units per line — rather than from a fudge factor, so that
    # a stockout means the policy was genuinely too thin and not that the
    # planner was handed a bad forecast.
    daily_units = {}
    for k in sku_keys:
        s = sku_by_key[k]
        cfg = PARAMS["banner"][s["banner"]]
        banner_orders = PARAMS["base_orders_per_day"] * cfg["order_share"]
        mean_lines = 1 + cfg["lines_lambda"]
        mean_qty = 1 + PARAMS["qty_mean_excess"]
        daily_units[k] = weights[k] * banner_orders * mean_lines * mean_qty

    # Textbook (s, S) policy, stated in weeks of demand rather than as a magic
    # fraction. The reorder point has to cover the demand that arrives while the
    # order is in transit AND while waiting for the next weekly review, plus
    # safety stock. An earlier version triggered at a flat 60% of the order-up-to
    # level, which happened to sit just below lead-time-plus-review demand, so
    # every replenishment arrived slightly too late and fill collapsed for a
    # reason that had nothing to do with the inventory being thin.
    on_hand = {}
    target_level = {}
    reorder_point = {}
    review_weeks = PARAMS["review_period_days"] / 7
    for k in sku_keys:
        s = sku_by_key[k]
        cover = PARAMS["banner"][s["banner"]]["cover_weeks"]
        ss = PARAMS["safety_stock_weeks"][s["velocity_band"]]
        nodes = placement[k]
        for node in nodes:
            kind = "FC1" if node == "FC1" else ("FC2" if node == "FC2"
                                                else "STORE")
            node_share = 0.55 if node == "FC1" else 0.45 / max(1, len(nodes) - 1)
            if len(nodes) == 1:
                node_share = 1.0
            weekly = daily_units[k] * 7 * node_share
            lead_weeks = PARAMS["lead_time_days"][kind] / 7
            rop = weekly * (lead_weeks + review_weeks + ss)
            eff_cover = cover * PARAMS["node_cover_multiplier"][kind]
            reorder_point[(k, node)] = max(1, int(round(rop)))
            tgt = max(2, int(round(rop + weekly * eff_cover)))
            target_level[(k, node)] = tgt
            on_hand[(k, node)] = tgt

    # --- ledgers ------------------------------------------------------------
    month_ledger = defaultdict(lambda: {"opening": 0, "receipts": 0,
                                        "shipped": 0, "adjustments": 0})
    opening_captured = set()
    fact_lines, fact_shipments, fact_receipts = [], [], []
    fact_orders = []
    labor_units = defaultdict(lambda: defaultdict(int))     # date -> fn -> units

    order_seq = 0
    receipt_seq = 0
    current_week = None
    pick_tables: dict = {}
    # Stock in transit. Replenishment raises on_hand on the day it ARRIVES, not
    # the day it is ordered — without this the lead time is a documented
    # parameter that changes nothing, and the ledger credits a receipt to the
    # month it lands in while the units were already available to ship in the
    # month before, which drives closing balances negative.
    pending = defaultdict(list)
    on_order = defaultdict(int)

    for dinfo in days:
        d = dinfo["full_date"]
        ym = dinfo["year_month"]

        # New week, new demand shocks.
        week = d.isocalendar()[:2]
        if week != current_week:
            current_week = week
            pick_tables = build_pick_tables(
                rng, sku_by_key, weights, PARAMS["weekly_shock_sigma"])

        # capture opening balances the first time we touch a month
        if ym not in opening_captured:
            opening_captured.add(ym)
            for key, qty in on_hand.items():
                month_ledger[(key[0], key[1], ym)]["opening"] = qty

        # --- arrivals: stock ordered earlier lands today ---------------------
        for k, node, qty in pending.pop(d, []):
            key = (k, node)
            on_hand[key] += qty
            on_order[key] -= qty
            month_ledger[(k, node, ym)]["receipts"] += qty
            labor_units[d]["receiving"] += qty
            labor_units[d]["putaway"] += qty

        # --- replenishment: weekly review, deterministic day of week --------
        if d.weekday() == 1:                       # Tuesday review
            for k in sku_keys:
                for node in placement[k]:
                    key = (k, node)
                    tgt = target_level[key]
                    # Reorder against inventory POSITION — on hand plus on
                    # order. Reordering against on-hand alone would order the
                    # same shortfall again at every review until the first
                    # delivery landed.
                    if on_hand[key] + on_order[key] <= reorder_point[key]:
                        qty = tgt - on_hand[key] - on_order[key]
                        kind = "FC1" if node == "FC1" else (
                            "FC2" if node == "FC2" else "STORE")
                        lead = PARAMS["lead_time_days"][kind]
                        recv = d + timedelta(days=lead)
                        if recv > PARAMS["period_end"]:
                            continue
                        receipt_seq += 1
                        # Dock-to-stock: receipt to putaway, in hours. Stores
                        # are slower because putaway competes with selling.
                        dts = max(1.0, rng.gauss(
                            6.5 if kind != "STORE" else 14.0, 2.4))
                        fact_receipts.append((
                            f"R{receipt_seq:08d}", int(recv.strftime("%Y%m%d")),
                            k, node, qty, round(dts, 2),
                            sku_by_key[k]["banner"]))
                        pending[recv].append((k, node, qty))
                        on_order[key] += qty

        # --- orders ---------------------------------------------------------
        n_orders = day_order_count(d, rng)
        for _ in range(n_orders):
            order_seq += 1
            banner = ("premium" if rng.random()
                      < PARAMS["banner"]["premium"]["order_share"]
                      else "offprice")
            cfg = PARAMS["banner"][banner]
            n_lines = 1 + min(6, int(rng.expovariate(1 / cfg["lines_lambda"])))

            # pick SKUs for this order, weighted, without replacement
            # A line is a STYLE and a quantity. The units are then spread across
            # the size run, because that is what the customer needs and what the
            # warehouse has to find. Three units of a style is an ordinary
            # basket; three units of one SIZE of one style is a wholesale order,
            # which is why the line cannot be grained at size.
            lines, subs = [], []
            seen = set()
            for _ in range(n_lines):
                for _attempt in range(6):
                    k = _weighted_pick(rng, banner, pick_tables)
                    style = style_of_sku[k]
                    if style not in seen:
                        seen.add(style)
                        break
                else:
                    continue
                qty = 1 + int(rng.expovariate(1 / PARAMS["qty_mean_excess"]))
                qty = min(qty, PARAMS["qty_cap"])
                unit_value = sku_by_key[k]["unit_value"]
                line_idx = len(lines)

                run = sizes_by_style[style]
                by_size = defaultdict(int)
                for _u in range(qty):
                    x = rng.random() * sum(sh for _, sh in run)
                    acc = 0.0
                    chosen = run[-1][0]
                    for sku_key, sh in run:
                        acc += sh
                        if x <= acc:
                            chosen = sku_key
                            break
                    by_size[chosen] += 1

                lines.append({"style_key": style, "qty_ordered": qty,
                              "unit_value": unit_value,
                              "sizes_requested": len(by_size)})
                for sku_key, units in sorted(by_size.items()):
                    subs.append({"line_idx": line_idx, "sku_key": sku_key,
                                 "qty_ordered": units,
                                 "unit_value": unit_value})
            if not lines:
                continue

            # Record error discovered at the pick face, drawn per line PER NODE.
            #
            # Per node matters. A discrepancy at the primary FC alone is not a
            # shortfall — the allocator simply reaches for the next node and
            # the line still ships complete, just in two parcels. It shows up
            # as a split, not as a short. Only when each pick face it touches
            # can also come up short does a large line get whittled down and
            # ship partially, and partial large lines are what pull unit fill
            # below line fill.
            phantom = {}
            for sb in subs:
                for node in placement[sb["sku_key"]]:
                    if rng.random() >= PARAMS["phantom_pick_rate"]:
                        continue
                    key = (sb["sku_key"], node)
                    held = on_hand.get(key, 0)
                    if held <= 0:
                        continue
                    phantom[key] = min(held, 1 + int(rng.expovariate(0.55)))

            plan, _ = allocate(subs, on_hand, placement, phantom)
            cf_units = counterfactual_single_node(subs, on_hand, placement)

            # The phantom units never existed. Write them off so the ledger
            # balances: they leave inventory as an adjustment, not as a
            # shipment.
            for key, units in phantom.items():
                on_hand[key] -= units
                month_ledger[(key[0], key[1], ym)]["adjustments"] += units

            order_id = f"O{order_seq:08d}"
            promise = d + timedelta(days=PARAMS["promise_days"][banner])
            nodes_used, order_units_ord, order_units_shp = set(), 0, 0
            order_value_ord, order_value_shp = 0.0, 0.0
            lines_full = 0

            # Commit the allocation at size grain, then roll the sizes back up
            # to the line the customer actually placed.
            line_shipped = defaultdict(int)
            line_nodes = defaultdict(set)
            line_sizes_filled = defaultdict(int)
            for si, sb in enumerate(subs):
                shipped_sub = sum(q for _, q in plan[si])
                line_shipped[sb["line_idx"]] += shipped_sub
                if shipped_sub == sb["qty_ordered"]:
                    line_sizes_filled[sb["line_idx"]] += 1
                for node, q in plan[si]:
                    nodes_used.add(node)
                    line_nodes[sb["line_idx"]].add(node)
                    on_hand[(sb["sku_key"], node)] -= q
                    month_ledger[(sb["sku_key"], node, ym)]["shipped"] += q
                    labor_units[d]["picking"] += q
                    labor_units[d]["packing"] += q
                    labor_units[d]["shipping"] += q

            for i, ln in enumerate(lines):
                shipped = line_shipped[i]
                order_units_ord += ln["qty_ordered"]
                order_units_shp += shipped
                order_value_ord += ln["qty_ordered"] * ln["unit_value"]
                order_value_shp += shipped * ln["unit_value"]
                if shipped == ln["qty_ordered"]:
                    lines_full += 1
                # Ship lag, and the honest consequence: a line sourced from a
                # store takes longer, so splits also cost service, not just
                # money.
                lag = 1 + int(rng.random() * 2)
                if any(n.startswith("S") for n in line_nodes[i]):
                    lag += 1
                ship_date = d + timedelta(days=lag)
                nodes_here = [n for n in NODE_ORDER if n in line_nodes[i]]
                fact_lines.append((
                    order_id, i + 1, ln["style_key"], banner,
                    int(d.strftime("%Y%m%d")),
                    int(ship_date.strftime("%Y%m%d")) if shipped else None,
                    int(promise.strftime("%Y%m%d")),
                    ln["qty_ordered"], shipped,
                    round(ln["unit_value"], 2),
                    nodes_here[0] if nodes_here else None,
                    len(nodes_here),
                    ln["sizes_requested"], line_sizes_filled[i],
                ))

            # One parcel per node used. This is the leak, and it is arithmetic,
            # not an assumption: two nodes means two parcels.
            parcel_cost = 0.0
            units_by_node = defaultdict(int)
            for i in plan:
                for n, q in plan[i]:
                    units_by_node[n] += q
            for node in sorted(nodes_used):
                units_here = units_by_node[node]
                cost = (PARAMS["parcel_base_cost"]
                        + PARAMS["parcel_cost_per_unit"] * units_here)
                if node.startswith("S"):
                    cost += PARAMS["store_pick_penalty"]
                parcel_cost += cost
                fact_shipments.append((
                    f"{order_id}-{node}", order_id, node,
                    int(d.strftime("%Y%m%d")), units_here, round(cost, 2),
                    banner))

            # What the SAME shipped units would have cost in ONE parcel from
            # the primary FC. Without this the split premium cannot be measured
            # honestly: split orders are systematically larger baskets, so
            # comparing the average cost of split orders against the average
            # cost of single-node orders compares two different populations and
            # flatters the split. The premium below is the incremental cost of
            # fragmenting THIS order, holding its contents fixed.
            one_parcel_cost = (
                PARAMS["parcel_base_cost"]
                + PARAMS["parcel_cost_per_unit"] * order_units_shp
            ) if order_units_shp else 0.0
            split_premium = round(parcel_cost - one_parcel_cost, 2)

            # Classification. Every order lands in exactly one state; there is
            # no fourth outcome and no null. validate.py re-derives this.
            if order_units_shp == 0:
                classification = "not_shipped"
            elif len(nodes_used) > 1:
                classification = "split"
            else:
                classification = "single_node"

            fact_orders.append((
                order_id, int(d.strftime("%Y%m%d")), banner, classification,
                len(lines), lines_full, order_units_ord, order_units_shp,
                round(order_value_ord, 2), round(order_value_shp, 2),
                len(nodes_used), round(parcel_cost, 2),
                round(one_parcel_cost, 2), split_premium,
                round(order_value_shp * PARAMS["banner"][banner]["gross_margin"],
                      2),
                cf_units,                       # counterfactual units shipped
                int(promise.strftime("%Y%m%d")),
            ))

        # --- month-end shrink ------------------------------------------------
        tomorrow = d + timedelta(days=1)
        if tomorrow.month != d.month or d == PARAMS["period_end"]:
            for key in sorted(on_hand):
                loss = int(on_hand[key] * PARAMS["monthly_shrink_rate"])
                if loss:
                    on_hand[key] -= loss
                    month_ledger[(key[0], key[1], ym)]["adjustments"] += loss

    return (fact_orders, fact_lines, fact_shipments, fact_receipts,
            month_ledger, labor_units, on_hand)


def _weighted_pick(rng, banner, tables):
    """Weighted SKU draw within a banner against this week's demand table."""
    keys, cum, total = tables[banner]
    x = rng.random() * total
    lo, hi = 0, len(cum) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if cum[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return keys[lo]


# ===========================================================================
# 6 · LABOR
# ===========================================================================

def build_labor(labor_units, wage_lookup):
    rows = []
    for d in sorted(labor_units):
        for fn in sorted(labor_units[d]):
            units = labor_units[d][fn]
            uph = PARAMS["units_per_labor_hour"][fn]
            hours = round(units / uph, 3)
            wage = wage_lookup[fn]
            rows.append((int(d.strftime("%Y%m%d")), fn, units, hours,
                         round(hours * wage, 2), wage, uph))
    return rows


def load_wages():
    """Map DC functions to the frozen BLS occupations. Picking and packing are
    the order-filler occupation; receiving and putaway are the material-mover
    occupation the brief anchors on; shipping carries the clerk rate."""
    import csv
    path = CLEAN_DIR / "anchor_labor.csv"
    by_role = {}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            by_role[r["role"]] = float(r["h_median"])
    return {
        "receiving": by_role["material_mover"],
        "putaway": by_role["material_mover"],
        "picking": by_role["order_filler"],
        "packing": by_role["order_filler"],
        "shipping": by_role["shipping_receiving_clerk"],
    }


# ===========================================================================
# 7 · WRITE
# ===========================================================================

def content_hash(con, tables=None) -> str:
    """Hash the DATA, not the file.

    Storage-engine internals are not the reproducibility claim; the contents
    are. Two identical datasets written by different DuckDB versions should
    agree, and they would not if the file bytes were hashed.

    The per-table digest is a row count plus the SUM of per-row hashes, which
    is deliberately ORDER-INDEPENDENT. Row order inside a table carries no
    meaning here — every fact table is keyed — so requiring a canonical sort
    would make the hash depend on something that is not part of the data. It
    also keeps the whole computation inside DuckDB rather than materialising
    two million rows through Python, which is what made the first version of
    this function unusable.
    """
    if tables is None:
        tables = sorted(t[0] for t in con.execute("SHOW TABLES").fetchall())
    h = hashlib.sha256()
    for table in tables:
        n, s = con.execute(
            f"SELECT COUNT(*), COALESCE(SUM(hash(to_json(t))::HUGEINT), 0) "
            f"FROM main.{table} t").fetchone()
        h.update(f"{table}:{n}:{s}".encode())
    return h.hexdigest()


def main() -> None:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)

    print(f"Cascadia Control Tower generator · seed {SEED}")
    print(f"Period {PARAMS['period_start']} to {PARAMS['period_end']}\n")

    days, styles, skus, nodes, banners = build_dimensions(rng)
    placement = assign_stocking(skus)
    weights = build_demand_weights(skus, rng)
    print(f"  {len(days)} days · {len(styles):,} styles · {len(skus):,} SKUs "
          f"(style x size) · {len(nodes)} nodes")

    print("  simulating ...")
    (f_orders, f_lines, f_ship, f_recv, ledger,
     labor_units, closing) = simulate(rng, days, styles, skus, placement,
                                      weights)
    print(f"  {len(f_orders):,} orders · {len(f_lines):,} lines · "
          f"{len(f_ship):,} shipments · {len(f_recv):,} receipts")

    wages = load_wages()
    f_labor = build_labor(labor_units, wages)

    # inventory snapshot rows, with conservation computed rather than asserted
    f_inv = []
    for (sku, node, ym), lg in sorted(ledger.items()):
        close = (lg["opening"] + lg["receipts"] - lg["shipped"]
                 - lg["adjustments"])
        f_inv.append((sku, node, ym, lg["opening"], lg["receipts"],
                      lg["shipped"], lg["adjustments"], close))

    if DB_PATH.exists():
        DB_PATH.unlink()
    con = duckdb.connect(str(DB_PATH))

    # Tables are created from DataFrames rather than row-by-row INSERTs. At
    # roughly two million fact rows the executemany path is not slow, it is
    # unusable — DuckDB's Python bindings bind each row individually, and the
    # first version of this script spent longer inserting than simulating.
    # Registering a frame hands the whole column to the engine at once.
    def write(name: str, rows, columns) -> None:
        frame = pd.DataFrame(rows, columns=columns)
        con.register("_staging", frame)
        con.execute(f"CREATE TABLE {name} AS SELECT * FROM _staging")
        con.unregister("_staging")
        print(f"    {name:24} {len(frame):>9,} rows")

    write("dim_date", [tuple(r.values()) for r in days],
          list(days[0].keys()))
    write("dim_sku", [tuple(r.values()) for r in skus], list(skus[0].keys()))
    write("dim_node", [tuple(r.values()) for r in nodes], list(nodes[0].keys()))
    write("dim_banner", [tuple(r.values()) for r in banners],
          list(banners[0].keys()))

    write("fact_order", f_orders, [
        "order_id", "order_date_key", "banner", "classification",
        "lines_ordered", "lines_filled", "units_ordered", "units_shipped",
        "value_ordered", "value_shipped", "nodes_used", "parcel_cost",
        "one_parcel_equivalent_cost", "split_premium", "gross_margin_dollars",
        "counterfactual_units_single_node", "promise_date_key"])

    write("dim_style", [tuple(r.values()) for r in styles],
          list(styles[0].keys()))

    write("fact_order_line", f_lines, [
        "order_id", "line_no", "style_key", "banner", "order_date_key",
        "ship_date_key", "promise_date_key", "qty_ordered", "qty_shipped",
        "unit_value", "primary_node", "nodes_on_line", "sizes_requested",
        "sizes_filled"])

    write("fact_shipment", f_ship, [
        "shipment_id", "order_id", "node_key", "ship_date_key", "units",
        "parcel_cost", "banner"])

    write("fact_receipt", f_recv, [
        "receipt_id", "receipt_date_key", "sku_key", "node_key", "units",
        "dock_to_stock_hours", "banner"])

    write("fact_inventory_month", f_inv, [
        "sku_key", "node_key", "year_month", "opening_units", "receipt_units",
        "shipped_units", "adjustment_units", "closing_units"])

    write("fact_labor_day", f_labor, [
        "date_key", "function", "units", "hours", "labor_cost", "hourly_wage",
        "units_per_hour"])

    # --- realized mix vs target -------------------------------------------
    r = con.execute("""
        SELECT
          SUM(units_shipped)::DOUBLE / SUM(units_ordered)          AS unit_fill,
          SUM(lines_filled)::DOUBLE  / SUM(lines_ordered)          AS line_fill,
          AVG(CASE WHEN units_shipped = units_ordered THEN 1.0 ELSE 0 END)
                                                                   AS order_fill,
          AVG(CASE WHEN classification = 'split' THEN 1.0 ELSE 0 END)
                                                                   AS split_rate,
          SUM(counterfactual_units_single_node)::DOUBLE
              / SUM(units_ordered)                                 AS cf_unit_fill,
          COUNT(*)                                                 AS orders
        FROM fact_order""").fetchone()
    realized = {"unit_fill": r[0], "line_fill": r[1], "order_fill": r[2],
                "split_rate": r[3], "counterfactual_unit_fill": r[4],
                "orders": r[5]}

    # Hash exactly the tables this script created. dbt later writes its own
    # models into the same file, and a hash taken over "whatever tables exist"
    # would then change every time the warehouse layer was rebuilt — reporting
    # a reproducibility failure that was really just dbt having run.
    base_tables = sorted(t[0] for t in con.execute("SHOW TABLES").fetchall())
    digest = content_hash(con, base_tables)
    con.close()

    print("\n  realized vs target")
    for k, tgt in PARAMS["targets"].items():
        print(f"    {k:22} {realized[k]:>7.2%}   target {tgt:>6.1%}   "
              f"delta {realized[k] - tgt:+.2%}")
    print(f"    {'counterfactual unit fill':22} "
          f"{realized['counterfactual_unit_fill']:>7.2%}   "
          f"(single-node-only rule)")
    print(f"\n  content hash {digest}")

    GOV_DIR.mkdir(parents=True, exist_ok=True)
    (GOV_DIR / "generator_run.json").write_text(json.dumps({
        "seed": SEED,
        "period": [str(PARAMS["period_start"]), str(PARAMS["period_end"])],
        "content_sha256": digest,
        "hashed_tables": base_tables,
        "realized": realized,
        "targets": PARAMS["targets"],
        "row_counts": {"fact_order": len(f_orders),
                       "fact_order_line": len(f_lines),
                       "fact_shipment": len(f_ship),
                       "fact_receipt": len(f_recv),
                       "fact_inventory_month": len(f_inv),
                       "fact_labor_day": len(f_labor)},
        "wage_basis": wages,
    }, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"  wrote {GOV_DIR / 'generator_run.json'}")
    print(f"  wrote {DB_PATH} "
          f"({DB_PATH.stat().st_size / 1_048_576:.1f} MB)")


if __name__ == "__main__":
    main()
