-- Service performance beyond fill: did it ship on time, and how fast did
-- inbound stock become sellable.
--
-- Grain: year_month x banner.
--
-- On-time is measured on SHIPPED lines only. An unshipped line is a fill
-- failure, not a lateness failure, and charging the same miss to both metrics
-- would double-count it -- which is precisely the sort of quiet
-- double-counting this module exists to surface.
--
-- Lines sourced from a store ship later, so splitting costs service as well as
-- money. That is visible here rather than argued.

with lines as (
    select * from {{ ref('stg_order_lines') }}
),

shipped as (
    select
        year_month,
        banner,
        count(*)                                      as lines_shipped,
        sum(is_on_time)                               as lines_on_time,
        sum(is_on_time) * 1.0 / nullif(count(*), 0)   as on_time_ship_rate,
        sum(case when is_multi_node = 1 and is_on_time = 1 then 1 else 0 end)
            * 1.0 / nullif(sum(is_multi_node), 0)     as on_time_rate_multi_node,
        sum(case when is_multi_node = 0 and is_on_time = 1 then 1 else 0 end)
            * 1.0 / nullif(sum(case when is_multi_node = 0 then 1 else 0 end), 0)
                                                      as on_time_rate_single_node
    from lines
    where ship_date_key is not null
    group by 1, 2
),

inbound as (
    select
        year_month,
        banner,
        count(*)                                      as receipts,
        sum(units)                                    as units_received,
        avg(dock_to_stock_hours)                      as avg_dock_to_stock_hours,
        max(dock_to_stock_hours)                      as max_dock_to_stock_hours
    from {{ ref('stg_receipts') }}
    group by 1, 2
)

select
    coalesce(s.year_month, i.year_month)              as year_month,
    coalesce(s.banner, i.banner)                      as banner,
    s.lines_shipped,
    s.lines_on_time,
    s.on_time_ship_rate,
    s.on_time_rate_single_node,
    s.on_time_rate_multi_node,
    i.receipts,
    i.units_received,
    i.avg_dock_to_stock_hours,
    i.max_dock_to_stock_hours

from shipped s
full outer join inbound i
    on s.year_month = i.year_month and s.banner = i.banner
