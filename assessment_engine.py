
"""
AquaGuard AI Assessment Engine
------------------------------
CSV ingestion, validation, descriptive statistics, hazard screening,
and project-context assessment.

Important:
The risk values produced here are transparent screening proxies.
They are NOT official CHRI, government, World Bank, or regulatory scores.
Replace/calibrate thresholds and indicator directions with validated
hazard-specific datasets before formal decision-making.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional
import numpy as np
import pandas as pd


HAZARD_ALIASES = {
    "Water": ["water", "water_quality", "waterlevel", "water_level", "groundwater", "drinking_water"],
    "Wildfire": ["wildfire", "forest_fire", "forestfire", "fire", "burn", "burn_area"],
    "Landslide": ["landslide", "landslides", "slope_failure", "debris_flow", "slope"],
    "Urban flooding": ["urban_flood", "urbanflood", "urban_flooding", "pluvial_flood", "stormwater", "drainage"],
    "River / flash flooding": ["flood", "flooding", "river_flood", "flash_flood", "riverlevel", "river_level"],
    "Drought / water stress": ["drought", "water_stress", "waterstress", "dryness"],
    "Extreme heat": ["heat", "heatwave", "heat_wave", "extreme_heat", "temperature"],
    "Coastal flooding / sea level": ["coastal", "coastal_flood", "storm_surge", "stormsurge", "sea_level"],
    "Storm / cyclone": ["storm", "cyclone", "wind_speed", "extreme_wind"],
}

SCENARIO_FACTOR = {"Low": 0.85, "Moderate": 1.00, "High": 1.15}
HORIZON_FACTOR = {"Near term": 0.90, "Mid century": 1.05, "Long term": 1.20}


def clean_column(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")


def detect_hazard(filename: str, columns: List[str]) -> str:
    text = " ".join([str(filename).lower()] + [str(c).lower() for c in columns])
    for hazard in [
        "Urban flooding", "Wildfire", "Landslide",
        "Coastal flooding / sea level", "Drought / water stress",
        "Extreme heat", "Storm / cyclone", "River / flash flooding", "Water"
    ]:
        if any(alias in text for alias in HAZARD_ALIASES[hazard]):
            return hazard
    return "General project data"


def _numeric_columns(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include=[np.number]).columns.tolist()


def _missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for c in df.columns:
        missing = int(df[c].isna().sum())
        rows.append({
            "Column": c,
            "Data type": str(df[c].dtype),
            "Missing": missing,
            "Missing %": round(100 * missing / max(len(df), 1), 2),
            "Unique": int(df[c].nunique(dropna=True)),
        })
    return pd.DataFrame(rows)


def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    numeric = _numeric_columns(df)
    if not numeric:
        return pd.DataFrame(columns=[
            "Indicator", "Count", "Mean", "Std", "Min", "P25", "Median", "P75", "Max"
        ])
    rows = []
    for c in numeric:
        s = pd.to_numeric(df[c], errors="coerce").dropna()
        if s.empty:
            continue
        rows.append({
            "Indicator": c,
            "Count": int(s.count()),
            "Mean": round(float(s.mean()), 4),
            "Std": round(float(s.std(ddof=1)) if len(s) > 1 else 0.0, 4),
            "Min": round(float(s.min()), 4),
            "P25": round(float(s.quantile(.25)), 4),
            "Median": round(float(s.median()), 4),
            "P75": round(float(s.quantile(.75)), 4),
            "Max": round(float(s.max()), 4),
        })
    return pd.DataFrame(rows)


def _normalize(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    valid = s.dropna()
    if valid.empty:
        return pd.Series(np.nan, index=s.index)
    lo, hi = float(valid.min()), float(valid.max())
    if np.isclose(lo, hi):
        return pd.Series(50.0, index=s.index)
    return ((s - lo) / (hi - lo) * 100).clip(0, 100)


def _location_columns(df: pd.DataFrame):
    cols = {clean_column(c): c for c in df.columns}
    lat = next((cols[x] for x in ["latitude", "lat"] if x in cols), None)
    lon = next((cols[x] for x in ["longitude", "lon", "lng", "long"] if x in cols), None)
    return lat, lon


def assess_dataset(
    df: pd.DataFrame,
    filename: str,
    selected_hazard: str = "Auto-detect",
    country: str = "Pakistan",
    climate_division: str = "Temperate",
    scenario: str = "Moderate",
    horizon: str = "Near term",
) -> Dict:
    work = df.copy()
    original_columns = list(work.columns)
    work.columns = [clean_column(c) for c in work.columns]

    hazard = (
        detect_hazard(filename, original_columns)
        if selected_hazard == "Auto-detect"
        else selected_hazard
    )

    numeric = _numeric_columns(work)
    stats = descriptive_statistics(work)
    missing = _missing_summary(work)
    lat, lon = _location_columns(work)

    numeric_signals = {}
    for c in numeric:
        n = _normalize(work[c])
        numeric_signals[c] = round(float(n.mean()), 2) if n.notna().any() else None

    valid_signals = [v for v in numeric_signals.values() if v is not None]
    base_score = float(np.mean(valid_signals)) if valid_signals else None

    # Context factor is intentionally modest. It is a screening adjustment,
    # not a calibrated climate model.
    sf = SCENARIO_FACTOR.get(scenario, 1.0)
    hf = HORIZON_FACTOR.get(horizon, 1.0)
    context_score = None if base_score is None else round(
        float(np.clip(base_score * sf * hf, 0, 100)), 1
    )

    if context_score is None:
        level = "Data review required"
    elif context_score >= 75:
        level = "Critical screening signal"
    elif context_score >= 55:
        level = "High screening signal"
    elif context_score >= 35:
        level = "Moderate screening signal"
    else:
        level = "Lower screening signal"

    top_indicators = sorted(
        [(k, v) for k, v in numeric_signals.items() if v is not None],
        key=lambda x: x[1],
        reverse=True,
    )[:10]

    return {
        "filename": filename,
        "hazard": hazard,
        "country": country,
        "climate_division": climate_division,
        "scenario": scenario,
        "horizon": horizon,
        "rows": len(work),
        "columns": len(work.columns),
        "numeric_columns": numeric,
        "numeric_count": len(numeric),
        "missing_cells": int(work.isna().sum().sum()),
        "missing_pct": round(float(work.isna().mean().mean() * 100), 2) if len(work.columns) else 0.0,
        "base_score": None if base_score is None else round(base_score, 1),
        "context_score": context_score,
        "level": level,
        "top_indicators": top_indicators,
        "stats": stats,
        "missing": missing,
        "lat_column": lat,
        "lon_column": lon,
        "dataframe": work,
    }


def combine_assessments(results: List[Dict]) -> Dict:
    valid = [r for r in results if r.get("context_score") is not None]
    if not valid:
        return {
            "overall_score": None,
            "overall_level": "Data review required",
            "hazards": pd.DataFrame(),
            "datasets": len(results),
            "rows": sum(r.get("rows", 0) for r in results),
        }

    overall = round(float(np.mean([r["context_score"] for r in valid])), 1)
    if overall >= 75:
        level = "Critical screening signal"
    elif overall >= 55:
        level = "High screening signal"
    elif overall >= 35:
        level = "Moderate screening signal"
    else:
        level = "Lower screening signal"

    hazard_rows = [{
        "Hazard": r["hazard"],
        "Dataset": r["filename"],
        "Rows": r["rows"],
        "Base score": r["base_score"],
        "Context-adjusted score": r["context_score"],
        "Signal": r["level"],
    } for r in valid]

    return {
        "overall_score": overall,
        "overall_level": level,
        "hazards": pd.DataFrame(hazard_rows),
        "datasets": len(results),
        "rows": sum(r.get("rows", 0) for r in results),
    }


def build_project_statistics(results: List[Dict], project: Dict) -> Dict:
    combined = combine_assessments(results)
    dataset_rows = []
    for r in results:
        dataset_rows.append({
            "Dataset": r["filename"],
            "Hazard": r["hazard"],
            "Rows": r["rows"],
            "Columns": r["columns"],
            "Numeric indicators": r["numeric_count"],
            "Missing %": r["missing_pct"],
            "Base score": r["base_score"],
            "Context-adjusted score": r["context_score"],
            "Signal": r["level"],
        })

    return {
        "project": project,
        "summary": combined,
        "datasets": pd.DataFrame(dataset_rows),
    }
