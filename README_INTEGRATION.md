# AquaGuard AI — additive PostgreSQL/PostGIS + Global City + Environmental/AI integration

This package extends the existing AquaGuard AI7 repository. It does not replace
`app.py`, `environment.py`, `assessment_engine.py`, or `assessment_ui.py`.

## What is added

- PostgreSQL/PostGIS persistence layer.
- Global city table designed for GeoNames `cities500.zip`.
- Spatial indexes for city and environmental observations.
- Environmental observations table.
- Risk-assessment and mitigation persistence tables.
- New environmental risk engine that consumes the existing AquaGuard five risk inputs plus environmental variables.
- Optional Groq AI interpretation/mitigation layer.
- New Streamlit tab: `PostGIS + GeoAI`.
- Global city map backed by PostGIS.

The existing AquaGuard risk, climate, sector, CHRI proxy, GHG and assessment-center tabs remain in place.

## 1. Create the database

Create a PostgreSQL database named `aquaguard`, enable PostGIS, and run:

    psql -d aquaguard -f sql/schema.sql

PostGIS stores and indexes geographic objects inside PostgreSQL, so the city and environmental layers can be queried spatially.

## 2. Configure secrets

Copy `secrets.toml.example` to the existing repository:

    .streamlit/secrets.toml

Fill in the PostgreSQL connection and optional Groq key. Do not commit the real file.

For Streamlit Community Cloud, paste the same configuration into the app's Secrets settings.

## 3. Add the dependencies

Merge `requirements-addon.txt` into the existing `requirements.txt`.
Do not delete the repository's existing dependencies.

## 4. Seed global cities

Set `DATABASE_URL`, for example:

    DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@HOST:5432/aquaguard

Then run:

    python seed_global_cities.py

By default this downloads GeoNames `cities500.zip`, loads the city records, and creates PostGIS point geometry and indexes.

If internet access is restricted, download the GeoNames file separately and run:

    python seed_global_cities.py --file cities500.zip

## 5. Patch the existing app

Copy these integration files into the AquaGuard repository root, then run:

    python app_patch.py

The patch is idempotent. Running it again will not add duplicate UI blocks.

## 6. Run AquaGuard

    streamlit run app.py

The original application remains the main app. The new `PostGIS + GeoAI` tab is additive.

## Architecture

    Existing AquaGuard Streamlit UI
             |
             +--> existing environment.py / assessment_engine.py
             |
             +--> NEW geoai_ui.py
                       |
                       +--> db.py --> PostgreSQL/PostGIS
                       |             +--> countries
                       |             +--> cities
                       |             +--> environmental_observations
                       |             +--> risk_assessments
                       |             +--> mitigation_actions
                       |
                       +--> risk_engine.py
                       |
                       +--> ai_risk_engine.py --> Groq

## Important model note

The AI integration defaults to `openai/gpt-oss-120b`. Groq's current documentation
lists this as a production model, while `llama-3.3-70b-versatile` was deprecated
for free/developer usage on August 16, 2026. If your account exposes another model,
set `GROQ_MODEL` in secrets.

## Data-quality note

The environmental risk engine is a transparent screening model. It is not an
official regulatory or CHRI score. Replace or calibrate its coefficients with
validated datasets and expert-reviewed methodology before professional decisions.
