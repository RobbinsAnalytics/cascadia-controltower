-- The diagnostic: shortfall and splitting are the same phenomenon.
--
-- Grain: velocity_band x banner.
--
-- Both rise together from fast movers to slow movers, because both come from
-- one cause -- inventory fragmented relative to what customers put in a basket.
-- Slow movers are ranged at two nodes rather than six, so a basket containing
-- one either reaches for a second node or goes short.
--
-- This is the evidence realism audit C tests: if splitting were uniform noise
-- rather than a pattern, these rates would be flat across the bands.

with lines as (
    select * from {{ ref('stg_order_lines') }}
)

select
    velocity_band,
    banner,

    count(*)                                          as lines,
    sum(qty_ordered)                                  as units_ordered,
    sum(qty_shipped)                                  as units_shipped,

    sum(case when line_state = 'zero'    then 1 else 0 end) * 100.0
        / count(*)                                    as pct_lines_zero,
    sum(case when line_state = 'partial' then 1 else 0 end) * 100.0
        / count(*)                                    as pct_lines_partial,
    sum(is_multi_node) * 100.0 / count(*)             as pct_lines_multi_node,

    sum(is_line_filled) * 1.0 / count(*)              as line_fill,
    sum(qty_shipped) * 1.0 / nullif(sum(qty_ordered), 0) as unit_fill,

    avg(sizes_requested)                              as avg_sizes_requested,
    avg(sizes_filled)                                 as avg_sizes_filled,
    avg(stocking_breadth)                             as avg_stocking_breadth

from lines
group by 1, 2
