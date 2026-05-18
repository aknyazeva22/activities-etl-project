-- models/staging/staging_degustation_current.sql

{{ config(
    materialized = 'table',
    post_hook = [
        "{{ macro_safe_drop_pk(this, 'pk_stg_activities') }}",
        "alter table {{ this }} add constraint pk_stg_activities primary key (activity_key)"
    ]
) }}


with staging_1 as (
    select *
    from {{ ref('staging_degustation_data') }}
),

ranked as (
    select
        *,
        row_number() over (
            partition by activity_key
            order by ingested_at desc, source_row_number desc
        ) as row_num
    from staging_1
)

select *
from ranked
where row_num = 1
