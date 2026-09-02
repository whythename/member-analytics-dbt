with months as (

    select distinct month_start, month_end
    from {{ ref('dim_date') }}
    where month_end <= (select max(checkin_date) from {{ ref('fct_checkin') }})

),

active as (

    select
        m.month_start,
        s.brand,
        d.plan,
        d.member_id,
        d.monthly_price
    from months m
    inner join {{ ref('dim_member') }} d
        on  d.valid_from <= m.month_end
        and (d.contract_end_date is null or d.contract_end_date >= m.month_end)
    inner join {{ ref('dim_studio') }} s
        on s.studio_id = d.home_studio_id

)

select
    month_start,
    brand,
    plan,
    count(distinct member_id)          as active_members,
    cast(sum(monthly_price) as decimal(12, 2)) as recurring_revenue
from active
group by 1, 2, 3
order by 1, 2, 3
