-- The module's headline: one dataset, three arithmetics, three answers.
--
-- Grain: year_month x banner.
--
-- Each rate is computed from the base quantities, never from another rate.
-- They disagree because they ask different questions, not because they were
-- measured at different times or on different populations:
--
--   unit fill  : how much of the demand did we move?          (most forgiving)
--   line fill  : how much of the assortment could we serve?
--   order fill : did the customer get what they asked for?    (strictest)
--
-- Order fill is arithmetically the lowest of the three, always: an order is
-- filled only if every line in it is. Stating that before anyone asks is the
-- difference between a finding and a defence.
--
-- Not-shipped orders stay in every denominator. They are demand the network
-- failed to serve, and removing them would make the service metrics measure
-- only the orders the network chose to succeed at.

with orders as (
    select * from {{ ref('stg_orders') }}
)

select
    year_month,
    banner,
    banner_name,
    positioning,

    count(*)                                          as orders,
    sum(lines_ordered)                                as lines_ordered,
    sum(lines_filled)                                 as lines_filled,
    sum(units_ordered)                                as units_ordered,
    sum(units_shipped)                                as units_shipped,
    sum(is_order_filled)                              as orders_filled,

    sum(units_shipped) * 1.0 / nullif(sum(units_ordered), 0)  as unit_fill,
    sum(lines_filled)  * 1.0 / nullif(sum(lines_ordered), 0)  as line_fill,
    sum(is_order_filled) * 1.0 / nullif(count(*), 0)          as order_fill,

    -- What the same demand would have achieved under a single-node-only rule,
    -- evaluated against the inventory position BEFORE each real allocation was
    -- committed. This is what turns "splitting is how the network achieves
    -- fill" from an assertion into a priced decision.
    sum(counterfactual_units_single_node) * 1.0
        / nullif(sum(units_ordered), 0)               as counterfactual_unit_fill,
    (sum(units_shipped) - sum(counterfactual_units_single_node)) * 1.0
        / nullif(sum(units_ordered), 0)               as unit_fill_bought_by_splitting,

    sum(is_split) * 1.0 / nullif(count(*), 0)         as split_rate,
    sum(is_not_shipped)                               as orders_not_shipped

from orders
group by 1, 2, 3, 4
