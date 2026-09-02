select
    studio_id as studio_key,
    studio_id,
    studio_name,
    brand,
    city,
    opened_at
from {{ ref('stg_studios') }}