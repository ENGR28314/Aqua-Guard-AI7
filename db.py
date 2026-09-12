"""PostgreSQL/PostGIS adapter for the existing AquaGuard AI application."""
from __future__ import annotations

import os
from typing import Optional

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def _secret_url() -> Optional[str]:
    # Supports Streamlit Cloud secrets and local environment variables.
    try:
        url = st.secrets.get("DATABASE_URL")
        if url:
            return str(url)
    except Exception:
        pass
    return os.getenv("DATABASE_URL")


def get_engine() -> Optional[Engine]:
    url = _secret_url()
    if not url:
        try:
            cfg = st.secrets.get("connections", {}).get("postgresql", {})
        except Exception:
            cfg = {}
        if cfg:
            host = cfg.get("host", "localhost")
            port = cfg.get("port", 5432)
            database = cfg.get("database")
            username = cfg.get("username")
            password = cfg.get("password")
            if database and username:
                from sqlalchemy.engine import URL
                url = URL.create(
                    "postgresql+psycopg2",
                    username=username,
                    password=password,
                    host=host,
                    port=int(port),
                    database=database,
                )
    if not url:
        return None
    try:
        return create_engine(url, pool_pre_ping=True, pool_recycle=1800)
    except Exception:
        return None


def db_available() -> bool:
    engine = get_engine()
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def postgis_available() -> bool:
    engine = get_engine()
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            value = conn.execute(text("SELECT PostGIS_Version()" )).scalar()
        return bool(value)
    except Exception:
        return False


def read_sql(query: str, params: Optional[dict] = None) -> pd.DataFrame:
    engine = get_engine()
    if engine is None:
        raise RuntimeError("PostgreSQL is not configured. Add DATABASE_URL or [connections.postgresql] to Streamlit secrets.")
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn, params=params or {})


def execute_sql(query: str, params: Optional[dict] = None) -> None:
    engine = get_engine()
    if engine is None:
        raise RuntimeError("PostgreSQL is not configured.")
    with engine.begin() as conn:
        conn.execute(text(query), params or {})


def load_city_points(country_iso3: Optional[str] = None, limit: int = 5000) -> pd.DataFrame:
    where = "WHERE country_iso3 = :country_iso3" if country_iso3 else ""
    params = {"country_iso3": country_iso3} if country_iso3 else {}
    query = f"""
        SELECT geoname_id, name, country_iso3, population, latitude, longitude,
               ST_AsEWKB(geom) AS geom
        FROM cities
        {where}
        ORDER BY population DESC NULLS LAST
        LIMIT {int(limit)}
    """
    return read_sql(query, params)


def load_city_risk_map(country_iso3: Optional[str], limit: int = 5000) -> pd.DataFrame:
    where = "WHERE c.country_iso3 = :country_iso3" if country_iso3 else ""
    params = {"country_iso3": country_iso3} if country_iso3 else {}
    query = f"""
        SELECT c.geoname_id, c.name, c.country_iso3, c.population,
               c.latitude, c.longitude,
               COALESCE(ra.risk_score, 0) AS risk_score,
               COALESCE(ra.risk_level, 'Not assessed') AS risk_level
        FROM cities c
        LEFT JOIN LATERAL (
            SELECT risk_score, risk_level
            FROM risk_assessments r
            WHERE r.city_geoname_id = c.geoname_id
            ORDER BY r.created_at DESC
            LIMIT 1
        ) ra ON TRUE
        {where}
        ORDER BY c.population DESC NULLS LAST
        LIMIT {int(limit)}
    """
    return read_sql(query, params)
