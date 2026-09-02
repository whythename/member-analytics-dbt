select
    checkin_id,
    checkin_ts
from {{ ref('stg_checkins') }}
where checkin_ts > current_date + interval 1 day
