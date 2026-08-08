select
    r.receipt_id,
    r.receipt_date_key,
    d.year_month,
    r.sku_key,
    s.style_key,
    s.velocity_band,
    r.node_key,
    n.node_kind,
    r.units,
    r.dock_to_stock_hours,
    r.banner

from {{ source('controltower', 'fact_receipt') }} r
join {{ source('controltower', 'dim_sku') }}  s on r.sku_key = s.sku_key
join {{ source('controltower', 'dim_node') }} n on r.node_key = n.node_key
join {{ source('controltower', 'dim_date') }} d on r.receipt_date_key = d.date_key
