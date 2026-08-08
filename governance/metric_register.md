# Certified metric register

<!-- GENERATED FILE — DO NOT EDIT BY HAND.
     Source: meta blocks on columns in dbt/models/marts/_marts.yml
     Regenerate: python src/build_metric_register.py
     Verify:     python src/build_metric_register.py --check -->

**8 certified · 3 exploratory.**

This register is generated from the `meta:` blocks on the dbt models
that compute these metrics — the same file that defines their tests.
Nothing here is typed twice, and
`python src/build_metric_register.py --check` fails the build if a
definition drifts from the model behind it.

**Certification is not a ranking.** An exploratory metric is not a bad
metric; it is a metric the business has agreed not to run on. Retaining
the other definitions and labelling them is the governance act. Quietly
deleting them would move the disagreement rather than resolve it.

| Metric | Tier | Grain | Owner | Computed by |
|---|---|---|---|---|
| Cost per order | **certified** | Order | Fulfillment finance | `fct_split_economics.cost_per_order` |
| Dock-to-stock | **certified** | Receipt | Inbound operations | `fct_service_monthly.avg_dock_to_stock_hours` |
| Inventory / sales ratio | **certified** | Month, whole network | Inventory planning | `fct_inventory_position.inventory_sales_ratio` |
| On-time ship | **certified** | Order line | DC operations | `fct_service_monthly.on_time_ship_rate` |
| Order fill | **certified** | Order | Fulfillment governance | `fct_fill_rate_monthly.order_fill` |
| Split premium | **certified** | Order | Fulfillment finance | `fct_split_economics.avg_split_premium` |
| Split rate | **certified** | Order | Network planning | `fct_fill_rate_monthly.split_rate` |
| Units per labor hour | **certified** | Month x warehouse function | DC operations | `fct_labor_productivity.actual_units_per_hour` |
| Counterfactual unit fill | exploratory | Unit | Fulfillment governance | `fct_fill_rate_monthly.counterfactual_unit_fill` |
| Line fill | exploratory | Order line | Merchandising analytics | `fct_fill_rate_monthly.line_fill` |
| Unit fill | exploratory | Unit | Operations | `fct_fill_rate_monthly.unit_fill` |

---

## Certified

### Cost per order

**Definition.** Total parcel cost divided by shipped orders. Orders that shipped nothing are excluded from both numerator and denominator.

- **Tier** · certified
- **Grain** · Order
- **Owner** · Fulfillment finance
- **Lineage** · `fact_order.parcel_cost, fact_order.classification`
- **Computed by** · `fct_split_economics.cost_per_order`
- **Version** · 1.0

**Why this tier.** An order with no parcel has no parcel cost. Including it would divide real cost across unreal volume and quietly flatter the figure.

**Version history.** 1.0 (2026-08-08) certified with not-shipped orders excluded, stated on the page next to the number.

### Dock-to-stock

**Definition.** Mean elapsed hours between goods being received and being available to pick.

- **Tier** · certified
- **Grain** · Receipt
- **Owner** · Inbound operations
- **Lineage** · `fact_receipt.dock_to_stock_hours`
- **Computed by** · `fct_service_monthly.avg_dock_to_stock_hours`
- **Version** · 1.0

**Why this tier.** Stock that has arrived but is not put away cannot fill an order, so this sits upstream of every fill rate on the register.

**Version history.** 1.0 (2026-08-08) certified at first publication.

### Inventory / sales ratio

**Definition.** End-of-month inventory valued at cost, divided by that month's sales at retail. Valuation follows the Census Monthly Retail Trade Survey so the figure means the same thing as the anchor.

- **Tier** · certified
- **Grain** · Month, whole network
- **Owner** · Inventory planning
- **Lineage** · `fact_inventory_month.closing_units, dim_sku.unit_cost, fact_order.value_shipped`
- **Computed by** · `fct_inventory_position.inventory_sales_ratio`
- **Version** · 1.0

**Why this tier.** The only metric here checked directly against a real published series. It sits below the Census sector band by design, because this is a fulfillment network and the sector figure includes store selling floors.

**Version history.** 1.0 (2026-08-08) certified at first publication.

### On-time ship

**Definition.** Order lines whose ship date fell on or before the promise date, divided by lines that shipped at all.

- **Tier** · certified
- **Grain** · Order line
- **Owner** · DC operations
- **Lineage** · `fact_order_line.ship_date_key, fact_order_line.promise_date_key`
- **Computed by** · `fct_service_monthly.on_time_ship_rate`
- **Version** · 1.0

**Why this tier.** An unshipped line is a fill failure, not a lateness failure. Counting it in both would charge one miss to two metrics, which is exactly the double-counting this module exists to surface.

**Version history.** 1.0 (2026-08-08) certified on shipped lines only.

### Order fill

**Definition.** Orders in which every line shipped its full ordered quantity, divided by all orders placed in the period, including orders that shipped nothing.

- **Tier** · certified
- **Grain** · Order
- **Owner** · Fulfillment governance
- **Lineage** · `fact_order_line.qty_ordered, fact_order_line.qty_shipped`
- **Computed by** · `fct_fill_rate_monthly.order_fill`
- **Version** · 1.0

**Why this tier.** A customer whose three-line order arrives missing a line did not receive 67% of an order; they received an incomplete order. Order fill is the only definition that says so.

**Version history.** 1.0 (2026-08-08) certified at first publication. Chosen over line and unit fill because it is the only one of the three that matches what the customer experiences.

### Split premium

**Definition.** Actual parcel cost minus what the same shipped units would have cost in a single parcel from the primary node.

- **Tier** · certified
- **Grain** · Order
- **Owner** · Fulfillment finance
- **Lineage** · `fact_order.parcel_cost, fact_order.one_parcel_equivalent_cost`
- **Computed by** · `fct_split_economics.avg_split_premium`
- **Version** · 1.0

**Why this tier.** Split orders are systematically larger baskets. Comparing the average cost of split orders against the average cost of single-node orders compares two different populations and flatters the split.

**Version history.** 1.0 (2026-08-08) certified on the incremental definition after the average-versus-average comparison was rejected.

### Split rate

**Definition.** Orders whose shipped units came from more than one fulfillment node, divided by all orders. Node count, not parcel count.

- **Tier** · certified
- **Grain** · Order
- **Owner** · Network planning
- **Lineage** · `fact_order.classification, fact_shipment.node_key`
- **Computed by** · `fct_fill_rate_monthly.split_rate`
- **Version** · 1.0

**Why this tier.** Node count responds to the allocation decision under review. Parcel count also responds to carton sizing and packaging rules, which are a different problem with a different owner.

**Version history.** 1.0 (2026-08-08) certified on the by-node definition. The by-parcel definition is retained as exploratory; see classification_rules.md.

### Units per labor hour

**Definition.** Units processed divided by paid labor hours, by function.

- **Tier** · certified
- **Grain** · Month x warehouse function
- **Owner** · DC operations
- **Lineage** · `fact_labor_day.units, fact_labor_day.hours`
- **Computed by** · `fct_labor_productivity.actual_units_per_hour`
- **Version** · 1.0

**Why this tier.** Costed at BLS Occupational Employment and Wage Statistics medians for the Seattle-Tacoma-Bellevue metro, May 2025, so cost per order is a real regional number rather than an invented rate.

**Version history.** 1.0 (2026-08-08) certified at first publication.

## Exploratory

### Counterfactual unit fill

**Definition.** Best units any single node could have shipped for each order, divided by units ordered.

- **Tier** · exploratory
- **Grain** · Unit
- **Owner** · Fulfillment governance
- **Lineage** · `fact_order.counterfactual_units_single_node`
- **Computed by** · `fct_fill_rate_monthly.counterfactual_unit_fill`
- **Version** · 1.0

**Why this tier.** A modelled alternative history, not a measurement. It prices the governance decision and must never be reported as achieved service.

**Version history.** 1.0 (2026-08-08) introduced with the module.

### Line fill

**Definition.** Order lines that shipped their full ordered quantity, divided by all order lines.

- **Tier** · exploratory
- **Grain** · Order line
- **Owner** · Merchandising analytics
- **Lineage** · `fact_order_line.qty_ordered, fact_order_line.qty_shipped`
- **Computed by** · `fct_fill_rate_monthly.line_fill`
- **Version** · 1.0

**Why this tier.** Useful as an assortment-coverage diagnostic, and it is what the merchant team has always read. Retaining it and labelling it is the governance act; quietly deleting it would move the disagreement rather than resolve it.

**Version history.** 1.0 (2026-08-08) retained as exploratory at first publication. Deliberately not retired.

### Unit fill

**Definition.** Units shipped divided by units ordered.

- **Tier** · exploratory
- **Grain** · Unit
- **Owner** · Operations
- **Lineage** · `fact_order_line.qty_ordered, fact_order_line.qty_shipped`
- **Computed by** · `fct_fill_rate_monthly.unit_fill`
- **Version** · 1.0

**Why this tier.** The most forgiving of the three and therefore the one most often quoted upward. Retained as a depth-of-stock diagnostic, explicitly not as the service number.

**Version history.** 1.0 (2026-08-08) retained as exploratory at first publication.

---

## The ad-hoc extraction pathology, shown and resolved

Before certification there were three fill rates in circulation and no
statement of which one the business ran on. Each was defensible to the
team that built it:

| Derivation | Who built it | Why it was defensible | What it cost |
|---|---|---|---|
| Unit fill | Operations | Measures how much of the demand physically moved, which is what a DC controls | The most forgiving of the three, so it was the number that travelled upward |
| Line fill | Merchandising | Measures assortment coverage, which is what a buyer can act on | Treats a missing line on a three-line order as a two-thirds success |
| Order fill | Finance | Measures whether the customer got what they asked for | Strictest, so it was the least quoted |

The cost was not licences or dashboards. It was that **the three teams
could not have the same conversation about the same week.** Operations
reported service improving while Finance reported it flat, and both
were arithmetically correct, so the meeting resolved nothing and the
split rate — which none of the three measured — went unexamined.

The resolution certifies order fill, retains the other two as
exploratory with the reason stated, and adds split rate to the
register so the cost of achieving fill is visible next to the fill
itself.

