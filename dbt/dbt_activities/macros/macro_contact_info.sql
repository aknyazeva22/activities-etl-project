{% macro macro_contact_info(model) %}
  "Adresse1" IS NOT NULL OR
  "Adresse1Suite" IS NOT NULL OR
  "Adresse partie 2" IS NOT NULL OR
  "Adresse partie 3" IS NOT NULL OR
  "N° de téléphone mobile" IS NOT NULL OR
  "N° de téléphone fixe" IS NOT NULL OR
  "Url du site web" IS NOT NULL OR
  "Adresse e-Mail" IS NOT NULL
{% endmacro %}
