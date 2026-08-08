-- One row. The whole operation, for the page's headline figures and for
-- anything that needs a single denominator.
--
-- Kept as a model rather than computed in the page build so that every number
-- a reader sees has the same lineage as every number a test checks.

with orders as (select * from {{ ref('stg_orders') }}),
     labor  as (select * from {{ ref('stg_labor') }})

select
    (select min(order_date) from orders)              as period_start,
    (select max(order_date) from orders)              as period_end,

    count(*)                                          as orders,
    sum(lines_ordered)                                as lines,
    sum(units_ordered)                                as units_ordered,
    sum(units_shipped)                                as units_shipped,
    sum(value_shipped)                                as sales_at_retail,
    sum(gross_margin_dollars)                         as gross_margin,

    sum(units_shipped) * 1.0 / nullif(sum(units_ordered), 0)  as unit_fill,
    sum(lines_filled)  * 1.0 / nullif(sum(lines_ordered), 0)  as line_fill,
    sum(is_order_filled) * 1.0 / nullif(count(*), 0)          as order_fill,
    sum(counterfactual_units_single_node) * 1.0
        / nullif(sum(units_ordered), 0)               as counterfactual_unit_fill,

    sum(is_split) * 1.0 / nullif(count(*), 0)         as split_rate,
    sum(is_not_shipped)                               as orders_not_shipped,

    sum(parcel_cost)                                  as parcel_cost,
    sum(split_premium)                                as split_premium,
    sum(split_premium) * 100.0 / nullif(sum(parcel_cost), 0)
                                                      as split_premium_pct_of_parcel,
    (select sum(labor_cost) from labor)               as labor_cost,
    (select sum(hours) from labor)                    as labor_hours,

    ((select sum(labor_cost) from labor) + sum(parcel_cost))
        / nullif(sum(value_shipped), 0)               as dc_cost_pct_of_sales,
    ((select sum(labor_cost) from labor) + sum(parcel_cost))
        / nullif(sum(case when is_not_shipped = 0 then 1 else 0 end), 0)
                                                      as cost_per_shipped_order

from orders
