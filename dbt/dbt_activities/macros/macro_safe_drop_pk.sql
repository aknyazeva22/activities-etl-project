{% macro macro_safe_drop_pk(relation, constraint_name) %}
  {% set backup_table = adapter.get_relation(
      database=relation.database,
      schema=relation.schema,
      identifier=relation.identifier ~ '__dbt_backup'
  ) %}

  {# drop PK on backup table if it exists #}
  {% if backup_table %}
    alter table {{ backup_table }} drop constraint if exists {{ adapter.quote(constraint_name) }};
  {% endif %}

  {# drop PK on the target relation #}
  alter table {{ relation }} drop constraint if exists {{ adapter.quote(constraint_name) }};

  {# drop leftover index that might have the same name as the constraint #}
  drop index if exists
    {{ adapter.quote(relation.schema) }}.{{ adapter.quote(constraint_name) }};
{% endmacro %}
