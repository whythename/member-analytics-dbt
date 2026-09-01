with source as (

    select * from {{ source('membership', 'members') }}

),

renamed as (

    select
        cast(member_id as varchar)                  as member_id,
        try_cast(birth_date as date)                as birth_date,
        lower(trim(cast(gender as varchar)))        as gender,
        cast(signup_date as date)                   as signup_date,
        cast(home_studio_id as varchar)             as home_studio_id,
        lower(trim(cast(source_channel as varchar))) as acquisition_channel
    from source

)

select * from renamed