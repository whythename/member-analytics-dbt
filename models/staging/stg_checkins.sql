with source as (

    select * from {{ source('access', 'checkins') }}

),

deduplicated as (

    select distinct * from source

),

renamed as (

    select
        cast(checkin_id as varchar) as checkin_id,
        cast(member_id as varchar)  as member_id,
        cast(studio_id as varchar)  as studio_id,
        cast(checkin_ts as timestamp) as checkin_ts,
        cast(checkin_ts as date)      as checkin_date
    from deduplicated

)

select * from renamed