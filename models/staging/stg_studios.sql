with source as (

    select * from {{ source('masterdata', 'studios') }}

),

renamed as (

    select
        cast(studio_id as varchar)   as studio_id,
        trim(cast(studio_name as varchar)) as studio_name,
        trim(cast(brand as varchar)) as brand,
        trim(cast(city as varchar))  as city,
        cast(opened_at as date)      as opened_at
    from source

)

select * from renamed
