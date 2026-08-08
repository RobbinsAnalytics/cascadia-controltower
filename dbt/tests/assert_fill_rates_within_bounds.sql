-- Every rate is a proportion. Anything outside [0, 1] means a numerator and
-- denominator came from different populations -- the exact defect the module
-- is about, so it must fail the build rather than appear on a chart.

select year_month, banner, 'unit_fill' as metric, unit_fill as value
from {{ ref('fct_fill_rate_monthly') }}
where unit_fill < 0 or unit_fill > 1

union all
select year_month, banner, 'line_fill', line_fill
from {{ ref('fct_fill_rate_monthly') }}
where line_fill < 0 or line_fill > 1

union all
select year_month, banner, 'order_fill', order_fill
from {{ ref('fct_fill_rate_monthly') }}
where order_fill < 0 or order_fill > 1

union all
select year_month, banner, 'split_rate', split_rate
from {{ ref('fct_fill_rate_monthly') }}
where split_rate < 0 or split_rate > 1

union all
select year_month, banner, 'counterfactual_unit_fill', counterfactual_unit_fill
from {{ ref('fct_fill_rate_monthly') }}
where counterfactual_unit_fill < 0 or counterfactual_unit_fill > 1
