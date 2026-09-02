with spine as (

    select cast(unnest(generate_series(
        date '2023-01-01',
        date '2026-12-31',
        interval 1 day
    )) as date) as date_day

)

select
    date_day,
    cast(date_trunc('month', date_day) as date) as month_start,
    last_day(date_day)                          as month_end,
    year(date_day)                              as year,
    month(date_day)                             as month,
    dayofweek(date_day)                         as day_of_week,
    dayofweek(date_day) in (0, 6)               as is_weekend
from spine
