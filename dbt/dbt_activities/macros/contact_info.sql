{% macro test_contact_info(model) %}
SELECT *
FROM {{ ref('staging_degustation_data') }}
WHERE address_line1 IS NULL
  AND address_line2 IS NULL
  AND address_line3 IS NULL
  AND address_line4 IS NULL
  AND modile_phone_number IS NULL
  AND landline_number IS NULL
  AND email IS NULL
  AND website IS NULL
{% endmacro %}
