-- models/staging/staging_degustation_data.sql

{{ config(
    materialized = 'table',
    post_hook = [
        "alter table {{ this }} add constraint pk_stg_activities primary key (activity_key)"
    ]
) }}

with src as (
  SELECT
  "Nom de l'offre touristique" AS offer_name,
  "Type d'offre" AS offer_type,
  "Adresse1" AS address_line1,
  "Adresse1Suite" AS address_line2,
  "Adresse partie 2" AS address_line3,
  "Adresse partie 3" AS address_line4,
  CAST("Code postal" AS {{ dbt.type_string() }}) AS postal_code,
  "Bureau distributeur de l'adresse postale" AS postal_office,
  "Commune du lieu de visite" AS city_name,
  "Cedex" AS cedex,
  "Code Insee de la Commune" AS city_code,
  "Latitude" AS latitude,
  "Longitude" AS longitude,
  "Situation de l'offre" AS transport_tips,
  "N° de téléphone mobile" AS mobile_phone_number,
  "N° de téléphone fixe" AS landline_number,
  "N° de fax" AS fax,
  "Adresse e-Mail" AS email,
  "Url du site web" AS website,
  "Url pour accéder à la vidéo" AS video_url,
  "Code Embed pour intégrer une vidéo" AS code_integration_video,
  "Type de plateforme/url" AS plateforme_type,
  "Widget tripadvisor" AS tripadvisor_widget,
  "Secteur d'activité" AS activity_sector,
  "Labels" AS quality_label,
  "Label tourisme handicap" AS accessibility_label,
  "Animal accepté: oui / non" AS animal_acceptance,
  "Complément information animal accepté" AS animal_acceptance_info,
  "Groupe accepté: oui / non" AS group_acceptance,
  "Nombre personnes max pour les groupes" AS maximum_group_size,
  "Nombre personnes min pour les groupes" AS minimum_group_size,
  "Langues parlées à l'accueil" AS languages,
  "Appellation pour les vins" AS wine_appellation,
  "Dégustations gratuites: oui / non" AS free_tastings,
  "Salle équipée pour dégustation: oui / non" AS tasting_room,
  "Vente à la propriété: oui / non" AS on_site_sales,
  "Durée de visite pour les individuels" AS duration_individual_visit,
  "Durée de visite pour les groupes" AS duration_group_visit,
  "Visites guidées proposées aux groupes en permanence: oui / no" AS regular_guided_group_visits,
  "Visites guidées proposées aux groupes sur demande: oui / non" AS guided_group_visit_on_request,
  "Visites libres proposées aux groupes en permanence: oui / non" AS regular_self_guided_group_visits,
  "Visites pédagogiques proposées aux groupes en permanence: oui" AS regular_educational_group_visits,
  "Visites guidées proposées aux individuels en permanence: oui " AS regular_guided_individual_visits,
  "Visites guidées proposées aux individuels sur demande: oui / " AS guided_individual_visit_on_request,
  "Langue(s) parlée(s) pendant les visites" AS languages_of_guided_visits,
  "Visites libres proposées aux individuels en permanence: oui / " AS regular_self_guided_individual_visits,
  "Les offres proposées" AS activity_type,
  CASE
      WHEN "Adresse1"        IS NOT NULL
       AND "Adresse1Suite"   IS NOT NULL
       AND "Adresse partie 2" IS NOT NULL
       AND "Adresse partie 3" IS NOT NULL
      THEN TRUE
      ELSE FALSE
  END AS is_address_given

  FROM {{ source('raw', 'raw_degustation_data') }}
  -- excludes activities with no contact info
  WHERE NOT {{ macro_contact_info() }}

),
normalized as (
  select
    *,
    lower(trim(coalesce(offer_name, '')))       as offer_name_norm,
    lower(trim(coalesce(address_line1, '')))    as address1_norm,
    lower(trim(coalesce(postal_code, '')))      as postal_code_norm,
    lower(trim(coalesce(city_name, '')))        as city_norm,
    cast(round(latitude::numeric, 5) as text)   as lat_norm,
    cast(round(longitude::numeric, 5) as text)  as lon_norm
  from src
)

select
  *,
  {{ dbt_utils.generate_surrogate_key([
      'offer_name_norm',
      'address1_norm',
      'postal_code_norm',
      'city_norm',
      'lat_norm',
      'lon_norm'
  ]) }} as activity_key
from normalized
  

