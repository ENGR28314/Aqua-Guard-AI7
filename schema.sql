-- AquaGuard AI additive PostgreSQL/PostGIS schema
-- Run once in the AquaGuard database.
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS countries (
    iso3 VARCHAR(3) PRIMARY KEY,
    iso2 VARCHAR(2),
    name TEXT NOT NULL,
    geom geometry(MULTIPOLYGON, 4326),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cities (
    geoname_id BIGINT PRIMARY KEY,
    name TEXT NOT NULL,
    ascii_name TEXT,
    country_iso2 VARCHAR(2),
    country_iso3 VARCHAR(3),
    admin1_code TEXT,
    population BIGINT DEFAULT 0,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    geom geometry(POINT, 4326),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS cities_geom_gix ON cities USING GIST (geom);
CREATE INDEX IF NOT EXISTS cities_country_idx ON cities (country_iso3);
CREATE INDEX IF NOT EXISTS cities_population_idx ON cities (population DESC);

CREATE TABLE IF NOT EXISTS environmental_observations (
    id BIGSERIAL PRIMARY KEY,
    country_iso3 VARCHAR(3),
    city_geoname_id BIGINT REFERENCES cities(geoname_id) ON DELETE SET NULL,
    observation_date DATE,
    temperature_anomaly DOUBLE PRECISION,
    precipitation_anomaly DOUBLE PRECISION,
    water_stress DOUBLE PRECISION,
    air_pollution DOUBLE PRECISION,
    water_pollution DOUBLE PRECISION,
    effluent_load DOUBLE PRECISION,
    ghg_tco2e DOUBLE PRECISION,
    exposure DOUBLE PRECISION,
    vulnerability DOUBLE PRECISION,
    adaptive_capacity DOUBLE PRECISION,
    sensitivity DOUBLE PRECISION,
    criticality DOUBLE PRECISION,
    source TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    geom geometry(POINT, 4326),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS environmental_obs_geom_gix
    ON environmental_observations USING GIST (geom);
CREATE INDEX IF NOT EXISTS environmental_obs_city_idx
    ON environmental_observations (city_geoname_id);
CREATE INDEX IF NOT EXISTS environmental_obs_country_idx
    ON environmental_observations (country_iso3);
CREATE INDEX IF NOT EXISTS environmental_obs_date_idx
    ON environmental_observations (observation_date DESC);

CREATE TABLE IF NOT EXISTS risk_assessments (
    id BIGSERIAL PRIMARY KEY,
    project_name TEXT,
    country_iso3 VARCHAR(3),
    city_geoname_id BIGINT REFERENCES cities(geoname_id) ON DELETE SET NULL,
    climate_division TEXT,
    scenario TEXT,
    horizon TEXT,
    sector TEXT,
    risk_score DOUBLE PRECISION,
    risk_level TEXT,
    chri_proxy DOUBLE PRECISION,
    ai_summary TEXT,
    inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    engine_version TEXT DEFAULT 'aquaguard-postgis-v1',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS risk_assessments_city_idx ON risk_assessments(city_geoname_id);
CREATE INDEX IF NOT EXISTS risk_assessments_country_idx ON risk_assessments(country_iso3);
CREATE INDEX IF NOT EXISTS risk_assessments_score_idx ON risk_assessments(risk_score DESC);

CREATE TABLE IF NOT EXISTS mitigation_actions (
    id BIGSERIAL PRIMARY KEY,
    risk_assessment_id BIGINT REFERENCES risk_assessments(id) ON DELETE CASCADE,
    hazard TEXT,
    sector TEXT,
    priority TEXT,
    action TEXT NOT NULL,
    rationale TEXT,
    esg_tags TEXT[],
    sdg_tags TEXT[],
    iso_tags TEXT[],
    estimated_effectiveness DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE OR REPLACE FUNCTION set_environmental_geom()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.city_geoname_id IS NOT NULL THEN
        SELECT geom INTO NEW.geom FROM cities WHERE geoname_id = NEW.city_geoname_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS environmental_geom_trigger ON environmental_observations;
CREATE TRIGGER environmental_geom_trigger
BEFORE INSERT OR UPDATE OF city_geoname_id
ON environmental_observations
FOR EACH ROW EXECUTE FUNCTION set_environmental_geom();
