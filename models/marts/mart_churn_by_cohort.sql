with member_span as (

    select
        member_id,
        min(signup_date) as signup_date,
        max(version_no)  as last_version
    from {{ ref('dim_member') }}
    group by 1

),

final_version as (

    select
        d.member_id,
        d.contract_end_date as churn_date
    from {{ ref('dim_member') }} d
    inner join member_span s
        on s.member_id = d.member_id
        and s.last_version = d.version_no

),

joined as (

    select
        cast(date_trunc('month', s.signup_date) as date) as cohort_month,
        s.member_id,
        f.churn_date,
        case when f.churn_date is null then null
             else date_diff('month', s.signup_date, f.churn_date) end as months_to_churn
    from member_span s
    inner join final_version f on f.member_id = s.member_id

),

observation_end as (

    select max(checkin_date) as as_of from {{ ref('fct_checkin') }}

)

select
    j.cohort_month,
    count(*)                                                          as cohort_size,
    count(*) filter (where j.months_to_churn < 3)                     as churned_3m,
    count(*) filter (where j.months_to_churn < 6)                     as churned_6m,
    count(*) filter (where j.months_to_churn < 12)                    as churned_12m,
    round(100.0 * count(*) filter (where j.months_to_churn < 3)  / count(*), 1) as churn_rate_3m_pct,
    round(100.0 * count(*) filter (where j.months_to_churn < 6)  / count(*), 1) as churn_rate_6m_pct,
    round(100.0 * count(*) filter (where j.months_to_churn < 12) / count(*), 1) as churn_rate_12m_pct,
    date_diff('month', j.cohort_month, o.as_of) >= 3  as is_mature_3m,
    date_diff('month', j.cohort_month, o.as_of) >= 6  as is_mature_6m,
    date_diff('month', j.cohort_month, o.as_of) >= 12 as is_mature_12m
from joined j
cross join observation_end o
group by j.cohort_month, o.as_of
order by j.cohort_month
