-- The classification stored on the order must be re-derivable from the
-- shipments alone. This is the ambiguity check: if the node count and the
-- label disagree, the rule did not resolve the case and the build stops
-- rather than guessing which one is right.

with derived as (
    select
        o.order_id,
        o.classification,
        count(distinct s.node_key) as nodes_from_shipments
    from {{ ref('stg_orders') }} o
    left join {{ ref('stg_shipments') }} s on o.order_id = s.order_id
    group by 1, 2
)

select
    order_id,
    classification,
    nodes_from_shipments,
    case
        when nodes_from_shipments = 0 then 'not_shipped'
        when nodes_from_shipments = 1 then 'single_node'
        else 'split'
    end as classification_implied_by_shipments
from derived
where classification <> case
        when nodes_from_shipments = 0 then 'not_shipped'
        when nodes_from_shipments = 1 then 'single_node'
        else 'split'
    end
