-- Latest version of each activity (one row per activity_key),
-- chosen by the most recent ingestion, then the last row in the file.

{{ config(
    post_hook = [
        "{{ safe_drop_pk(this, 'pk_int_activities_current') }}",
        "alter table {{ this }} add constraint pk_int_activities_current primary key (activity_key)"
    ]
) }}

with activities as (
    select *
    from {{ ref('stg_paysdelaloire__activities') }}
),

ranked as (
    select
        *,
        row_number() over (
            partition by activity_key
            order by ingested_at desc, source_row_number desc
        ) as row_num
    from activities
)

-- same columns as the staging model, without the helper row_num
select {{ dbt_utils.star(from=ref('stg_paysdelaloire__activities')) }}
from ranked
where row_num = 1
