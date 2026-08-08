-- The second finding: the same allocation rule produces different economics
-- depending on which banner the order belongs to.
--
-- Grain: banner x classification.
--
-- The split premium is near-identical in dollars across the banners and wildly
-- different as a share of the margin it eats. That is why there is no single
-- correct split threshold, and it is a governance finding rather than a
-- modelling inconvenience.
--
-- Not-shipped orders are EXCLUDED from cost per order. An order with no parcel
-- has no parcel cost, and including it would divide real cost across unreal
-- volume. They remain in every fill rate, where they belong.

with orders as (
    select * from {{ ref('stg_orders') }}
    where classification <> 'not_shipped'
)

select
    banner,
    banner_name,
    positioning,
    classification,

    count(*)                                          as orders,
    sum(units_shipped)                                as units_shipped,
    avg(value_shipped)                                as avg_order_value,
    avg(parcel_cost)                                  as avg_parcel_cost,
    avg(one_parcel_equivalent_cost)                   as avg_one_parcel_cost,
    avg(split_premium)                                as avg_split_premium,
    sum(split_premium)                                as total_split_premium,
    avg(gross_margin_dollars)                         as avg_gross_margin,
    sum(gross_margin_dollars)                         as total_gross_margin,

    -- The number the decision turns on.
    avg(split_premium / nullif(gross_margin_dollars, 0))
                                                      as split_premium_pct_of_margin,
    sum(parcel_cost) / nullif(count(*), 0)            as cost_per_order

from orders
group by 1, 2, 3, 4
