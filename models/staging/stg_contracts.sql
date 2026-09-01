with source as (

    select * from {{ source('membership', 'contracts') }}

),

renamed as (

    select
        cast(contract_id as varchar)      as contract_id,
        cast(member_id as varchar)        as member_id,
        lower(trim(cast(plan as varchar))) as plan,
        cast(monthly_price as decimal(8, 2)) as monthly_price,
        cast(start_date as date)          as start_date,
        try_cast(nullif(trim(cast(end_date as varchar)), '') as date) as end_date,
        nullif(trim(cast(cancel_reason as varchar)), '')  as cancel_reason
    from source

)

select * from renamed