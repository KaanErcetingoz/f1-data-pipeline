-- One row per race: extracts race details and the winning driver and constructor.

WITH races AS (

    SELECT unnest(payload -> '$.MRData.RaceTable.Races[*]') as race
    FROM {{ source('raw', 'race_winners') }}


),

RENAMED AS (

    SELECT
        (race ->> '$.season')::integer as season,
        (race ->> '$.round')::integer as round,
        race ->> '$.raceName' as race_name,
        race ->> '$.Circuit.circuitId' as circuit_id,
        race ->> '$.Circuit.circuitName' as circuit_name,
        race ->> '$.Circuit.Location.country' as country,
        (race ->> '$.date')::date as race_date,
        race ->> '$.Results[0].Driver.driverId' as driver_id,
        race ->> '$.Results[0].Driver.givenName' as driver_given_name,
        race ->> '$.Results[0].Driver.familyName' as  driver_family_name,
        race ->> '$.Results[0].Constructor.constructorId' as constructor_id,
        race ->> '$.Results[0].Constructor.name' as constructor_name
    FROM races
)

select * from renamed