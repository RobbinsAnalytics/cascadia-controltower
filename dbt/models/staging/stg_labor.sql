-- Labor by day and function, costed at frozen BLS Seattle-metro medians.
-- The wage is carried on the row rather than joined at report time, so a
-- reader can see that the dollars come from a real published rate.

select
    l.date_key,
    d.full_date                                   as work_date,
    d.year_month,
    d.is_peak_season,
    l.function,
    l.units,
    l.hours,
    l.labor_cost,
    l.hourly_wage,
    l.units_per_hour,
    l.labor_cost / nullif(l.units, 0)             as labor_cost_per_unit

from {{ source('controltower', 'fact_labor_day') }} l
join {{ source('controltower', 'dim_date') }} d on l.date_key = d.date_key
