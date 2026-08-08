-- Fragmenting an order can never be cheaper than shipping it whole. A split
-- pays at least one extra parcel base rate, so the premium is bounded below by
-- zero on every order.
--
-- A negative premium would mean the cost model had inverted -- that the page's
-- central claim about the leak pointed the wrong way -- so this is checked
-- rather than assumed.

select
    order_id,
    classification,
    nodes_used,
    parcel_cost,
    one_parcel_equivalent_cost,
    split_premium
from {{ ref('stg_orders') }}
where split_premium < 0
   or (classification = 'split' and split_premium <= 0)
