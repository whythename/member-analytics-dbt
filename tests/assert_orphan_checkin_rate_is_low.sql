with counts as (

    select
        (select count(*) from {{ ref('stg_checkins') }}) as source_rows,
        (select count(*) from {{ ref('fct_checkin') }})  as fact_rows

)

select
    source_rows,
    fact_rows,
    source_rows - fact_rows as dropped_rows,
    round(100.0 * (source_rows - fact_rows) / source_rows, 3) as dropped_pct
from counts
where 1.0 * (source_rows - fact_rows) / source_rows > 0.01
