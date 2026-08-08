-- The counterfactual is the best any SINGLE node could have done, so it can
-- never beat what the network actually shipped -- the real allocator had every
-- single-node option available to it and more.
--
-- If this ever fired, the counterfactual would be measuring something other
-- than what it claims, and the module's central claim -- that splitting is how
-- the network achieves fill -- would be resting on a broken comparison.

select
    year_month,
    banner,
    unit_fill,
    counterfactual_unit_fill,
    counterfactual_unit_fill - unit_fill as impossible_gain
from {{ ref('fct_fill_rate_monthly') }}
where counterfactual_unit_fill > unit_fill + 1e-9
