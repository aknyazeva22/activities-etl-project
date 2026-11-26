{#
  True when an activity has at least one contact detail
  (address, phone, website or email).
  Uses the renamed (staging) column names, not the raw source names.
#}
{% macro has_contact_info() %}
  (
    address_line1 is not null
    or address_line2 is not null
    or address_line3 is not null
    or address_line4 is not null
    or mobile_phone_number is not null
    or landline_number is not null
    or website is not null
    or email is not null
  )
{% endmacro %}
