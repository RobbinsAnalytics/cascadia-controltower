-- One row per order line, with the style attributes that explain WHY a line
-- fails. The three line states are mutually exclusive and exhaustive.
--
-- `partial` is the state that matters most. It is the only one that separates
-- unit fill from line fill: a line shipping four of six units is a total
-- failure to line fill but two thirds of a success to unit fill.

select
    l.order_id,
    l.line_no,
    l.style_key,
    s.category,
    s.velocity_band,
    s.stocking_breadth,
    l.banner,
    l.order_date_key,
    d.year_month,
    l.ship_date_key,
    l.promise_date_key,
    l.qty_ordered,
    l.qty_shipped,
    l.unit_value,
    l.qty_ordered * l.unit_value                  as value_ordered,
    l.qty_shipped * l.unit_value                  as value_shipped,
    l.primary_node,
    l.nodes_on_line,
    l.sizes_requested,
    l.sizes_filled,

    case
        when l.qty_shipped = 0                  then 'zero'
        when l.qty_shipped = l.qty_ordered      then 'full'
        else 'partial'
    end                                           as line_state,

    case when l.qty_shipped = l.qty_ordered then 1 else 0 end
                                                  as is_line_filled,
    case when l.nodes_on_line > 1 then 1 else 0 end
                                                  as is_multi_node,

    -- On-time is only meaningful for a line that shipped. An unshipped line is
    -- a fill failure, not a lateness failure, and counting it as late would
    -- charge the same miss to two different metrics.
    case
        when l.ship_date_key is null then null
        when l.ship_date_key <= l.promise_date_key then 1
        else 0
    end                                           as is_on_time

from {{ source('controltower', 'fact_order_line') }} l
join {{ source('controltower', 'dim_style') }} s on l.style_key = s.style_key
join {{ source('controltower', 'dim_date') }}  d on l.order_date_key = d.date_key
