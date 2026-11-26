{% macro macro_contact_info(model) %}
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
