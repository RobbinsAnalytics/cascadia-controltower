-- The prescriptive layer: what a split-cost threshold would actually catch.
--
-- Grain: threshold x banner.
--
-- Read it as a policy dial. At threshold T, an order whose split premium
-- exceeds T would be held as an exception rather than split automatically.
-- The curve shows how many orders that is, what it would have saved, and --
-- the part that matters -- how much fill would have been LOST, because the
-- units rescued by those splits would not have shipped.
--
-- Exception counts fall monotonically as T rises. validate.py asserts that,
-- and asserts the curve is not degenerate.
--
-- The two banners need different thresholds. That is the finding.

with thresholds as (
    select * from (values (4), (5), (6), (7), (8), (10), (12), (15), (20))
        as t(threshold_usd)
),

splits as (
    select * from {{ ref('stg_orders') }}
    where classification = 'split'
),

banner_totals as (
    select banner, count(*) as total_split_orders
    from splits group by 1
)

select
    t.threshold_usd,
    s.banner,
    s.banner_name,

    count(*)                                          as orders_above_threshold,
    count(*) * 100.0 / bt.total_split_orders          as pct_of_split_orders,
    sum(s.split_premium)                              as premium_above_threshold,
    avg(s.split_premium)                              as avg_premium_above,
    avg(s.value_shipped)                              as avg_order_value_above,

    -- What holding these orders would cost in service. The units on a split
    -- order beyond what one node could have supplied are units that only
    -- shipped BECAUSE the order was split.
    sum(s.units_shipped - s.counterfactual_units_single_node)
                                                      as units_at_risk,
    avg(s.split_premium / nullif(s.gross_margin_dollars, 0))
                                                      as avg_premium_pct_of_margin

from thresholds t
join splits s        on s.split_premium > t.threshold_usd
join banner_totals bt on bt.banner = s.banner
group by 1, 2, 3, bt.total_split_orders
