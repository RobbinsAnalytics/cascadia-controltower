-- The monthly inventory ledger, valued both ways.
--
-- Valuation matters for realism audit A. Census reports retail inventories at
-- COST while sales are at retail, so the ratio compared against the anchor
-- must use inventory at cost over sales at retail. Carrying both columns makes
-- the choice visible instead of buried in a coefficient.

select
    i.sku_key,
    s.style_key,
    s.size,
    s.category,
    s.velocity_band,
    s.banner,
    i.node_key,
    n.node_kind,
    i.year_month,
    i.opening_units,
    i.receipt_units,
    i.shipped_units,
    i.adjustment_units,
    i.closing_units,
    i.closing_units * s.unit_cost                 as closing_value_at_cost,
    i.closing_units * s.unit_value                as closing_value_at_retail,

    -- Restated conservation identity. If this is ever non-zero the ledger is
    -- broken, and a dbt test asserts exactly that.
    i.opening_units + i.receipt_units - i.shipped_units - i.adjustment_units
        - i.closing_units                         as conservation_error

from {{ source('controltower', 'fact_inventory_month') }} i
join {{ source('controltower', 'dim_sku') }}  s on i.sku_key = s.sku_key
join {{ source('controltower', 'dim_node') }} n on i.node_key = n.node_key
