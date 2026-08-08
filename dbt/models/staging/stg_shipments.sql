select
    sh.shipment_id,
    sh.order_id,
    sh.node_key,
    n.node_name,
    n.node_kind,
    n.cost_rank,
    sh.ship_date_key,
    d.year_month,
    sh.units,
    sh.parcel_cost,
    sh.banner

from {{ source('controltower', 'fact_shipment') }} sh
join {{ source('controltower', 'dim_node') }} n on sh.node_key = n.node_key
join {{ source('controltower', 'dim_date') }} d on sh.ship_date_key = d.date_key
