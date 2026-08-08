-- Opening + receipts - shipped - adjustments must equal closing, on every
-- SKU-node-month. No tolerance: these are whole units, and a discrepancy means
-- the ledger lost track of physical goods.
--
-- This test earned its place. An earlier version of the generator credited
-- receipts to the ledger on the arrival date while raising on-hand on the
-- ORDER date, and 10,186 sku-months closed negative. Nothing in the fill rates
-- or the cost model looked wrong; only conservation caught it.

select
    sku_key,
    node_key,
    year_month,
    opening_units,
    receipt_units,
    shipped_units,
    adjustment_units,
    closing_units,
    conservation_error
from {{ ref('stg_inventory') }}
where conservation_error <> 0
   or closing_units < 0
