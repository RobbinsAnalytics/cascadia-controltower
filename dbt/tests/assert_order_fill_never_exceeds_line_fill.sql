-- Order fill can never exceed line fill. An order counts as filled only if
-- every line in it is filled, so the strictest definition is arithmetically
-- bounded by the looser one.
--
-- Only this ordering is guaranteed. Unit fill versus line fill depends on
-- whether shortfalls land on large or small lines, so it is NOT asserted here
-- -- asserting it would be encoding an assumption as an invariant, which is
-- the failure this module is about.
--
-- A tiny tolerance absorbs floating-point noise in the division, nothing more.

select
    year_month,
    banner,
    order_fill,
    line_fill,
    order_fill - line_fill as excess
from {{ ref('fct_fill_rate_monthly') }}
where order_fill > line_fill + 1e-9
