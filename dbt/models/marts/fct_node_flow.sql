-- Where units actually ship from, and what each node costs to ship from.
--
-- Grain: year_month x node.
--
-- The network is not symmetric. The primary FC does most of the volume at the
-- lowest unit cost; stores are the expensive last resort that rescues orders
-- the FC cannot fill. Seeing the tail nodes carry small volume at high cost is
-- the shape that makes the split premium believable.

select
    year_month,
    node_key,
    node_name,
    node_kind,
    cost_rank,
    banner,

    count(*)                                          as shipments,
    sum(units)                                        as units,
    sum(parcel_cost)                                  as parcel_cost,
    sum(parcel_cost) / nullif(count(*), 0)            as cost_per_parcel,
    sum(parcel_cost) / nullif(sum(units), 0)          as cost_per_unit

from {{ ref('stg_shipments') }}
group by 1, 2, 3, 4, 5, 6
