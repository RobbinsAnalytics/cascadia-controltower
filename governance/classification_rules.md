# Classification rules

Every rule the module runs on, stated in full, with its edge cases and the tie
handling that fails the build rather than guessing.

`validate.py` re-derives each of these independently from the base facts. It
does not import the generator's implementation — a suite that imports the thing
it is checking proves only that the code agrees with itself.

---

## 1 · Fulfillment classification

Every order lands in **exactly one** of three states. There is no fourth
outcome, and there is no null.

| State | Rule |
|---|---|
| `single_node` | The order shipped at least one unit, and every shipped unit came from one node. |
| `split` | The order shipped at least one unit, and shipped units came from more than one node. |
| `not_shipped` | The order shipped zero units. |

**`not_shipped` is a real state, not a dodge.** An order that shipped nothing
cannot be split or not-split, because splitting is a property of how something
was shipped. Forcing it into `single_node` would inflate the single-node
population with orders that were never fulfilled at all, and quietly improve
every cost-per-order figure computed against it.

### What fails the build

- Any order whose classification is null, or is not one of the three above.
- Any order classified `split` with `nodes_used <= 1`, or `single_node` with
  `nodes_used != 1`, or `not_shipped` with `units_shipped > 0`.
- Any shipped order line whose node is null. **This is the ambiguity case.** A
  unit that moved must have moved from somewhere; if the pipeline cannot say
  where, the run stops rather than assigning it to the most likely node.

---

## 2 · Split by node, or split by parcel?

**This is a genuine definitional fork, and it is the same disease as the fill
rate.** Two defensible definitions, different numbers, and most operations have
never written down which one they mean.

| Definition | Counts as a split when… | Who reads it this way |
|---|---|---|
| **By node** *(certified)* | Units ship from more than one **location** | Network and inventory teams — it measures fragmentation of stock |
| By parcel *(exploratory)* | The customer receives more than one **box** | Customer experience and carrier-spend teams — it measures what the customer sees and what the carrier bills |

They come apart in both directions. One node shipping an oversized order in two
cartons is one node and two parcels. Two nodes each shipping one carton is two
nodes and two parcels.

**Certified: split by node.** The module's argument is about *where inventory
sits* and what fragmenting it costs. Node count is the measure that responds to
the allocation decision under review; parcel count also responds to carton
sizing and packaging rules, which are a different problem with a different
owner.

Parcel-based splitting is retained and reported, not dropped. Retaining it and
labelling it is the governance act.

---

## 3 · The allocation rule that produces splits

The generator contains no notion of a split. Splits are the observed
consequence of this rule, which is stated here as it would be to a merchant:

1. **If one node can ship the whole order, use the cheapest such node.** Nodes
   rank by cost to serve — primary FC, second FC, then stores.
2. **Otherwise fill line by line, most valuable line first, from the cheapest
   node that has stock.**
3. **Anything no node holds is short-shipped.** It is not backordered, not
   substituted, and not silently dropped from the denominator.

Rule 2 is where splits come from. Reaching for a second node is not a decision
the model makes about splitting; it is what is left when rule 1 cannot be
satisfied.

### Why splits concentrate rather than scatter

Two structural causes, both visible in the data:

- **Stocking breadth by velocity band.** Fast movers are carried at all six
  nodes; mid movers at four; **slow movers at the primary FC only.** Any basket
  mixing a slow mover with a fast mover that has stocked out at the primary FC
  must reach for a second node. Slow-moving SKUs also skew expensive, so those
  are exactly the lines worth rescuing.
- **Cover depth by banner.** The off-price banner runs leaner weeks of cover
  than the premium banner, so it stocks out more often, so it splits more often.
  This is a consequence of the inventory policy, not a rule about banners.

---

## 4 · The three fill rates

One dataset, three arithmetics, three different questions. All three are
computed from `qty_ordered` and `qty_shipped` on the order line — none is
assigned, and none is derived from another.

**An order line is a style and a quantity; stock is held per style AND size.**
That distinction is what lets the three numbers differ at all. A line for three
units spreads across the size run, and the warehouse must find each size
separately, so the line commonly ships two of three rather than all or nothing.
Hold stock at style level instead and every line becomes all-or-nothing, at
which point unit fill and line fill collapse to within half a point of each
other — the same number wearing two names. Size brokenness is also simply the
commonest reason a real retail line ships incomplete.

| Metric | Numerator | Denominator | The question it answers |
|---|---|---|---|
| **Order fill** *(certified)* | Orders where every line shipped complete | All orders | "Did the customer get what they asked for?" |
| Line fill *(exploratory)* | Order lines shipped complete | All order lines | "How much of the assortment could we serve?" |
| Unit fill *(exploratory)* | Units shipped | Units ordered | "How much of the demand did we move?" |

They diverge because a partly-filled order is a total failure to order fill, a
partial success to line fill, and nearly a success to unit fill. **Order fill is
always the lowest of the three** and unit fill the highest — arithmetically
guaranteed, and worth stating before anyone asks whether the numbers were
picked.

**Certified: order fill.** It is the only one of the three that matches what the
customer experiences. A customer whose three-line order arrives missing a line
did not receive 67% of an order; they received an incomplete order. The other
two are diagnostics: line fill points at assortment coverage, unit fill at depth
of stock. Both are useful and neither is the service number.

### What fails the build

Each fill rate must reconcile to its own definition, recomputed from the base
facts. A fill rate that cannot be independently reproduced from
`fact_order_line` is a fail, not a rounding note.

---

## 5 · Not-shipped orders and the denominator

`not_shipped` orders stay in the denominator of all three fill rates. They are
demand the network failed to serve, and removing them would make the service
metrics measure only the orders the network chose to succeed at.

They are excluded from **cost per order**, because an order with no parcel has
no parcel cost, and including it would divide real cost across unreal volume.
Both treatments are stated on the page next to the numbers they affect.

---

## 6 · The counterfactual

For every order the simulation also records what the **same order against the
same inventory position** would have shipped under a single-node-only rule —
the best any one node could have done alone.

This exists because the module's central claim is that *splitting is how the
network achieves fill*. Without the counterfactual that claim is an assertion.
With it, the cost of forbidding splits is a number, and the governance decision
can be priced instead of argued.

The counterfactual is evaluated against the inventory position **before** the
actual allocation is committed, so it is a genuine alternative history rather
than a comparison against already-depleted stock.
