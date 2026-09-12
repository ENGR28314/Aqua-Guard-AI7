"""Load a global GeoNames cities500.zip file into PostGIS.

Usage:
  python seed_global_cities.py --url https://download.geonames.org/export/dump/cities500.zip

The script downloads only when --file is not supplied. Run it once against your
PostgreSQL/PostGIS database; Streamlit should query the resulting table at runtime.
"""
from __future__ import annotations

import argparse
import io
import os
import zipfile

import pandas as pd
import requests
import pycountry
from sqlalchemy import create_engine, text

COLS = [
    "geoname_id", "name", "ascii_name", "alternatenames", "latitude", "longitude",
    "feature_class", "feature_code", "country_iso2", "cc2", "admin1_code", "admin2_code",
    "admin3_code", "admin4_code", "population", "elevation", "dem", "timezone", "modification_date"
]


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise SystemExit("Set DATABASE_URL before running this script.")
    return url


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://download.geonames.org/export/dump/cities500.zip")
    parser.add_argument("--file", help="Local cities500.zip path")
    parser.add_argument("--chunk-size", type=int, default=10000)
    args = parser.parse_args()

    if args.file:
        raw = open(args.file, "rb").read()
    else:
        response = requests.get(args.url, timeout=120)
        response.raise_for_status()
        raw = response.content

    engine = create_engine(get_database_url())
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        name = next(n for n in zf.namelist() if n.endswith(".txt"))
        with zf.open(name) as fh:
            first = True
            for chunk in pd.read_csv(
                fh, sep="\t", header=None, names=COLS, chunksize=args.chunk_size,
                usecols=["geoname_id", "name", "ascii_name", "country_iso2", "admin1_code", "population", "latitude", "longitude"],
                dtype={"geoname_id": "int64", "population": "Int64"},
            ):
                chunk = chunk.rename(columns={"country_iso2": "country_iso2"})
                chunk["country_iso3"] = chunk["country_iso2"].map(
                    lambda code: (pycountry.countries.get(alpha_2=str(code)).alpha_3
                                  if pycountry.countries.get(alpha_2=str(code)) else None)
                )
                chunk.to_sql("cities", engine, if_exists="append", index=False, method="multi")
                print(f"Loaded {len(chunk):,} cities")

    with engine.begin() as conn:
        # Populate the country dimension used by the existing AquaGuard country selector.
        for c in pycountry.countries:
            conn.execute(
                text("""
                    INSERT INTO countries (iso3, iso2, name) VALUES (:iso3, :iso2, :name)
                    ON CONFLICT (iso3) DO NOTHING
                """),
                {"iso3": c.alpha_3, "iso2": c.alpha_2, "name": c.name},
            )
        conn.execute(text("""
            UPDATE cities
            SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
            WHERE geom IS NULL;
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS cities_geom_gix ON cities USING GIST (geom)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS cities_country_idx ON cities(country_iso3)"))

    print("Global city load complete.")


if __name__ == "__main__":
    main()
