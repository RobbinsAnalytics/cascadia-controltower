-- Inventory position, in the form realism audit A checks against Census.
--
-- Grain: year_month.
--
-- Inventory is valued at COST and sales at RETAIL, because that is how the
-- Census Monthly Retail Trade Survey reports the inventories/sales ratio. A
-- ratio built from retail-valued inventory would sit about 60% higher and
-- would silently fail to mean the same thing as the anchor.
--
-- The level is expected to sit BELOW the Census department-store band, and
-- that is not a defect. Census covers entire department stores, most of whose
-- stock sits on selling floors serving walk-in customers this module never
-- simulates. Audit A therefore requires this ratio to be strictly inside the
-- sector figure, above a floor, and to move with the real series seasonally.

with inv as (
    select
        year_month,
        sum(closing_units)                            as closing_units,
        sum(closing_value_at_cost)                    as inventory_at_cost,
        sum(closing_value_at_retail)                  as inventory_at_retail
    from {{ ref('stg_inventory') }}
    group by 1
),

sales as (
    select
        year_month,
        sum(value_shipped)                            as sales_at_retail,
        sum(units_shipped)                            as units_shipped
    from {{ ref('stg_orders') }}
    group by 1
)

select
    inv.year_month,
    cast(split_part(inv.year_month, '-', 1) as integer)  as year,
    cast(split_part(inv.year_month, '-', 2) as integer)  as month,
    inv.closing_units,
    inv.inventory_at_cost,
    inv.inventory_at_retail,
    sales.sales_at_retail,
    sales.units_shipped,

    inv.inventory_at_cost / nullif(sales.sales_at_retail, 0)
                                                      as inventory_sales_ratio,
    sales.sales_at_retail * 12.0 / nullif(inv.inventory_at_cost, 0)
                                                      as annualised_turns

from inv
join sales using (year_month)
