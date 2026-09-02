select
    member_id,
    version_no,
    valid_from,
    valid_to
from {{ ref('dim_member') }} a
where exists (
    select 1
    from {{ ref('dim_member') }} b
    where b.member_id = a.member_id
      and b.member_key != a.member_key
      and b.valid_from < a.valid_to
      and b.valid_to   > a.valid_from
)