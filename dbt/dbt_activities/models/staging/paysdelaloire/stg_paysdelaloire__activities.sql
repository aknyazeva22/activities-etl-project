-- Staging model for Pays de la Loire "Activités touristiques".
-- Renames source columns to English snake_case, adds is_address_given,
-- keeps only activities with contact details and adds activity_key.
--
-- TODO(ADR-001): the column mapping below still follows the former
-- degustation dataset. Check every source column against the activities
-- schema. Degustation-only columns (wine_appellation, free_tastings,
-- tasting_room, on_site_sales) probably have no equivalent: remove them
-- here and in _paysdelaloire__models.yml, and add the activity columns.

with source as (
    select * from {{ source('paysdelaloire', 'activities') }}
),

renamed as (
    select
        "Nom de l'offre touristique" as offer_name,
        "Type d'offre" as offer_type,
        "Adresse1" as address_line1,
        "Adresse1Suite" as address_line2,
        "Adresse partie 2" as address_line3,
        "Adresse partie 3" as address_line4,
        cast("Code postal" as {{ dbt.type_string() }}) as postal_code,
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
        source_row_number,
        ingestion_id,
        ingested_at,
        source_file_name,
        source_system,
        source_hash
    from source
),

filtered as (
    select
        *,
        (
            address_line1 is not null
            or address_line2 is not null
            or address_line3 is not null
            or address_line4 is not null
        ) as is_address_given
    from renamed
    -- keep only activities with at least one contact detail
    where {{ has_contact_info() }}
)

select
    *,
    -- best-effort business key: normalised name + address
    {{ dbt_utils.generate_surrogate_key([
        "lower(trim(coalesce(offer_name, '')))",
        "lower(trim(coalesce(address_line1, '')))",
        "lower(trim(coalesce(address_line2, '')))",
        "lower(trim(coalesce(address_line3, '')))",
        "lower(trim(coalesce(address_line4, '')))",
        "lower(trim(coalesce(postal_code, '')))",
        "lower(trim(coalesce(city_name, '')))",
    ]) }} as activity_key
from filtered
