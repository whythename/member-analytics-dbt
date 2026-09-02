with contracts as (

    select * from {{ ref('stg_contracts') }}

),

members as (

    select * from {{ ref('stg_members') }}

),

versioned as (

    select
        member_id,
        contract_id,
        plan,
        monthly_price,
        end_date                                as contract_end_date,
        cancel_reason,
        start_date                              as valid_from,
        coalesce(
            lead(start_date) over (partition by member_id order by start_date),
            date '2999-12-31'
        )                                       as valid_to,
        row_number() over (partition by member_id order by start_date) as version_no
    from contracts

)

select
    md5(v.member_id || '|' || cast(v.valid_from as varchar)) as member_key,
    v.member_id,
    m.birth_date,
    m.gender,
    m.signup_date,
    m.home_studio_id,
    m.acquisition_channel,
    v.contract_id,
    v.plan,
    v.monthly_price,
    v.contract_end_date,
    v.cancel_reason,
    v.valid_from,
    v.valid_to,
    v.version_no,
    v.valid_to = date '2999-12-31'  as is_current
from versioned v
inner join members m on m.member_id = v.member_id
