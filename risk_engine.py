"""Additive environmental risk engine.

The existing AquaGuard calculations remain the primary project-level engine.
This module adds environmental variables that can be stored per city/project.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict


def _clip(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, float(value)))


@dataclass
class EnvironmentalRiskInputs:
    exposure: float = 60
    vulnerability: float = 55
    adaptive_capacity: float = 50
    sensitivity: float = 55
    criticality: float = 65
    temperature_anomaly: float = 0.0
    precipitation_anomaly: float = 0.0
    water_stress: float = 0.0
    air_pollution: float = 0.0
    water_pollution: float = 0.0
    effluent_load: float = 0.0
    ghg_intensity: float = 0.0


def calculate_environmental_risk(values: EnvironmentalRiskInputs) -> dict:
    climate = _clip(abs(values.temperature_anomaly) / 3.0 * 100)
    precipitation = _clip(abs(values.precipitation_anomaly) / 50.0 * 100)
    environmental_pressure = (
        0.18 * climate
        + 0.12 * precipitation
        + 0.18 * values.water_stress
        + 0.15 * values.air_pollution
        + 0.12 * values.water_pollution
        + 0.10 * values.effluent_load
        + 0.15 * values.ghg_intensity
    )
    social_pressure = (
        0.25 * values.exposure
        + 0.25 * values.vulnerability
        + 0.20 * values.sensitivity
        + 0.15 * values.criticality
        + 0.15 * (100 - values.adaptive_capacity)
    )
    total = _clip(0.55 * social_pressure + 0.45 * environmental_pressure)
    level = "High" if total >= 70 else "Moderate" if total >= 40 else "Low"
    return {
        "risk_score": round(total, 2),
        "risk_level": level,
        "environmental_pressure": round(environmental_pressure, 2),
        "social_pressure": round(social_pressure, 2),
        "inputs": asdict(values),
    }
