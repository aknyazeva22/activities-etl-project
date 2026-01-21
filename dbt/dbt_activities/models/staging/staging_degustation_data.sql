-- models/staging/staging_degustation_data.sql

{{ config(
    materialized = 'table',
    post_hook = [
        "{{ macro_safe_drop_pk(this, 'pk_stg_activities') }}",
        "alter table {{ this }} add constraint pk_stg_activities primary key (activity_key)"
    ]
) }}

with src as (
    select
        "Nom de l'offre touristique" as offer_name,
        "Type d'offre" as offer_type,
        "Adresse1" as address_line1,
        "Adresse1Suite" as address_line2,
        "Adresse partie 2" as address_line3,
        "Adresse partie 3" as address_line4,
        CAST("Code postal" as {{ dbt.type_string() }}) as postal_code,
        "Bureau distributeur de l'adresse postale" as postal_office,
        "Commune du lieu de visite" as city_name,
        "Cedex" as cedex,
        "Code Insee de la Commune" as city_code,
        "Latitude" as latitude,
        "Longitude" as longitude,
        "Situation de l'offre" as transport_tips,
        "N° de téléphone mobile" as mobile_phone_number,
        "N° de téléphone fixe" as landline_number,
        "N° de fax" as fax,
        "Adresse e-Mail" as email,
        "Url du site web" as website,
        "Url pour accéder à la vidéo" as video_url,
        "Code Embed pour intégrer une vidéo" as code_integration_video,
        "Type de plateforme/url" as plateforme_type,
        "Widget tripadvisor" as tripadvisor_widget,
        "Secteur d'activité" as activity_sector,
        "Labels" as quality_label,
        "Label tourisme handicap" as accessibility_label,
        "Animal accepté: oui / non" as animal_acceptance,
        "Complément information animal accepté" as animal_acceptance_info,
        "Groupe accepté: oui / non" as group_acceptance,
        "Nombre personnes max pour les groupes" as maximum_group_size,
        "Nombre personnes min pour les groupes" as minimum_group_size,
        "Langues parlées à l'accueil" as languages,
        "Appellation pour les vins" as wine_appellation,
        "Dégustations gratuites: oui / non" as free_tastings,
        "Salle équipée pour dégustation: oui / non" as tasting_room,
        "Vente à la propriété: oui / non" as on_site_sales,
        "Durée de visite pour les individuels" as duration_individual_visit,
        "Durée de visite pour les groupes" as duration_group_visit,
        "Visites guidées proposées aux groupes en permanence: oui / no" as regular_guided_group_visits,
        "Visites guidées proposées aux groupes sur demande: oui / non" as guided_group_visit_on_request,
        "Visites libres proposées aux groupes en permanence: oui / non" as regular_self_guided_group_visits,
        "Visites pédagogiques proposées aux groupes en permanence: oui" as regular_educational_group_visits,
        "Visites guidées proposées aux individuels en permanence: oui " as regular_guided_individual_visits,
        "Visites guidées proposées aux individuels sur demande: oui / " as guided_individual_visit_on_request,
        "Langue(s) parlée(s) pendant les visites" as languages_of_guided_visits,
        "Visites libres proposées aux individuels en permanence: oui / " as regular_self_guided_individual_visits,
        "Les offres proposées" as activity_type,
        COALESCE(
            "Adresse1" is not NULL
            and "Adresse1Suite" is not NULL
            and "Adresse partie 2" is not NULL
            and "Adresse partie 3" is not NULL, FALSE
        ) as is_address_given

    from {{ source('raw', 'raw_degustation_data') }}
    -- excludes activities with no contact info
    where not {{ macro_contact_info() }}

),

normalized as (
    select
        *,
        LOWER(TRIM(COALESCE(offer_name, ''))) as offer_name_norm,
        LOWER(TRIM(COALESCE(address_line1, ''))) as address1_norm,
        LOWER(TRIM(COALESCE(postal_code, ''))) as postal_code_norm,
        LOWER(TRIM(COALESCE(city_name, ''))) as city_norm,
        CAST(ROUND(CAST(latitude as numeric), 5) as text) as lat_norm,
        CAST(ROUND(CAST(longitude as numeric), 5) as text) as lon_norm
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
