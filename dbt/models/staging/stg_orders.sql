-- One row per order, with the calendar attached and the derived economics
-- that every downstream mart needs.
--
-- `split_premium` is the INCREMENTAL cost of fragmenting this order: what it
-- actually cost in parcels, minus what the same shipped units would have cost
-- in one. Split orders are systematically larger baskets, so comparing split
-- averages against single-node averages compares two different populations
-- and flatters the split.

select
    o.order_id,
    o.order_date_key,
    d.full_date                                   as order_date,
    d.year_month,
    d.year,
    d.month,
    d.is_peak_season,
    o.banner,
    b.banner_name,
    b.positioning,
    o.classification,
    o.lines_ordered,
    o.lines_filled,
    o.units_ordered,
    o.units_shipped,
    o.value_ordered,
    o.value_shipped,
    o.nodes_used,
    o.parcel_cost,
    o.one_parcel_equivalent_cost,
    o.split_premium,
    o.gross_margin_dollars,
    o.counterfactual_units_single_node,
    o.promise_date_key,

    case when o.units_shipped = o.units_ordered then 1 else 0 end
                                                  as is_order_filled,
    case when o.classification = 'split' then 1 else 0 end
                                                  as is_split,
    case when o.classification = 'not_shipped' then 1 else 0 end
                                                  as is_not_shipped

from {{ source('controltower', 'fact_order') }} o
join {{ source('controltower', 'dim_date') }}   d on o.order_date_key = d.date_key
join {{ source('controltower', 'dim_banner') }} b on o.banner = b.banner_key
