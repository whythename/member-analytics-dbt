select
    c.checkin_id,
    d.member_key,
    c.member_id,
    s.studio_key,
    c.studio_id,
    c.checkin_date,
    c.checkin_ts,
    c.studio_id != d.home_studio_id             as is_guest_visit,
    date_diff('day', d.signup_date, c.checkin_date) as days_since_signup
from {{ ref('stg_checkins') }} c
inner join {{ ref('dim_member') }} d
    on  c.member_id = d.member_id
    and c.checkin_ts >= d.valid_from
    and c.checkin_ts <  d.valid_to
inner join {{ ref('dim_studio') }} s
    on c.studio_id = s.studio_id
