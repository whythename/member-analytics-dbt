select
    contract_id,
    start_date,
    end_date
from {{ ref('stg_contracts') }}
where end_date is not null
  and end_date <= start_date