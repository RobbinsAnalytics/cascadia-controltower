-- Units per labor hour, costed at real regional wages.
--
-- Grain: year_month x function.
--
-- The wage is the frozen BLS Occupational Employment and Wage Statistics
-- median for the Seattle-Tacoma-Bellevue metro, May 2025 -- SOC 53-7062 for
-- material handling, 53-7065 for order filling, 43-5071 for shipping clerks.
-- Nothing here is an invented rate, which is what makes cost per order a real
-- number rather than an illustrative one.

select
    year_month,
    function,

    sum(units)                                        as units,
    sum(hours)                                        as hours,
    sum(labor_cost)                                   as labor_cost,
    max(hourly_wage)                                  as hourly_wage,
    max(units_per_hour)                               as standard_units_per_hour,

    sum(units) / nullif(sum(hours), 0)                as actual_units_per_hour,
    sum(labor_cost) / nullif(sum(units), 0)           as labor_cost_per_unit,
    sum(case when is_peak_season then hours else 0 end) as peak_season_hours

from {{ ref('stg_labor') }}
group by 1, 2
