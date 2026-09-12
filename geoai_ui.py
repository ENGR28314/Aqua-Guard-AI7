"""Streamlit UI that adds PostGIS + global city + AI risk functionality."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from db import db_available, postgis_available, load_city_risk_map
from risk_engine import EnvironmentalRiskInputs, calculate_environmental_risk
from ai_risk_engine import explain_risk


def render_geoai_panel(
    country: str,
    country_iso3: str,
    project_name: str,
    climate_division: str,
    scenario: str,
    horizon: str,
    exposure: float,
    vulnerability: float,
    adaptive_capacity: float,
    sensitivity: float,
    criticality: float,
) -> None:
    st.subheader("🌐 PostGIS + Global City + Environmental AI")
    st.caption("Additive integration: the existing AquaGuard assessment tabs remain unchanged.")

    a, b, c = st.columns(3)
    a.metric("PostgreSQL", "Connected" if db_available() else "Not configured")
    b.metric("PostGIS", "Enabled" if postgis_available() else "Not detected")
    b.caption("Spatial storage and queries")
    c.metric("Selected country", country)

    if not db_available():
        st.info(
            "Connect PostgreSQL first. The original AquaGuard app continues to work without the database. "
            "Once DATABASE_URL is configured and the schema/city data are loaded, this panel becomes live."
        )
        return

    st.markdown("### Global country/city risk map")
    limit = st.slider("Cities to display", 100, 5000, 1000, step=100)
    try:
        city_df = load_city_risk_map(country_iso3 or None, limit=limit)
    except Exception as exc:
        st.error(f"City query failed: {exc}")
        return

    if city_df.empty:
        st.warning("No city records were found. Run seed_global_cities.py against the configured database.")
    else:
        city_df["risk_score"] = pd.to_numeric(city_df["risk_score"], errors="coerce").fillna(0)
        fig = px.scatter_geo(
            city_df,
            lat="latitude",
            lon="longitude",
            size="population",
            color="risk_score",
            hover_name="name",
            hover_data={
                "country_iso3": True,
                "population": True,
                "risk_score": ":.1f",
                "latitude": ":.4f",
                "longitude": ":.4f",
            },
            color_continuous_scale="RdYlGn_r",
            range_color=(0, 100),
            projection="natural earth",
            title="PostGIS city risk layer",
        )
        fig.update_layout(height=600, margin=dict(l=0, r=0, t=55, b=0))
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            city_df[["name", "country_iso3", "population", "risk_score", "risk_level"]],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("### Environmental variables")
    e1, e2, e3, e4 = st.columns(4)
    temperature_anomaly = e1.number_input("Temperature anomaly (°C)", -10.0, 10.0, 0.0, 0.1)
    precipitation_anomaly = e2.number_input("Precipitation anomaly (%)", -100.0, 100.0, 0.0, 1.0)
    water_stress = e3.slider("Water stress", 0, 100, 40)
    air_pollution = e4.slider("Air pollution", 0, 100, 40)
    e5, e6, e7 = st.columns(3)
    water_pollution = e5.slider("Water pollution", 0, 100, 30)
    effluent_load = e6.slider("Effluent load", 0, 100, 25)
    ghg_intensity = e7.slider("GHG intensity", 0, 100, 35)

    values = EnvironmentalRiskInputs(
        exposure=exposure,
        vulnerability=vulnerability,
        adaptive_capacity=adaptive_capacity,
        sensitivity=sensitivity,
        criticality=criticality,
        temperature_anomaly=temperature_anomaly,
        precipitation_anomaly=precipitation_anomaly,
        water_stress=water_stress,
        air_pollution=air_pollution,
        water_pollution=water_pollution,
        effluent_load=effluent_load,
        ghg_intensity=ghg_intensity,
    )
    result = calculate_environmental_risk(values)

    m1, m2, m3 = st.columns(3)
    m1.metric("Environmental risk", f"{result['risk_score']:.1f}/100")
    m2.metric("Environmental pressure", f"{result['environmental_pressure']:.1f}/100")
    m3.metric("Priority", result["risk_level"])

    drivers = pd.DataFrame({
        "Driver": ["Exposure", "Vulnerability", "Sensitivity", "Criticality", "Water stress", "Air pollution", "Water pollution", "Effluent", "GHG"],
        "Score": [exposure, vulnerability, sensitivity, criticality, water_stress, air_pollution, water_pollution, effluent_load, ghg_intensity],
    })
    st.plotly_chart(
        px.bar(drivers, x="Driver", y="Score", range_y=[0, 100], title="Environmental risk drivers"),
        use_container_width=True,
    )

    if st.button("🤖 Generate AI risk interpretation", type="primary"):
        context = {
            "project_name": project_name,
            "country": country,
            "country_iso3": country_iso3,
            "climate_division": climate_division,
            "scenario": scenario,
            "horizon": horizon,
            "environmental_risk": result,
        }
        with st.spinner("Generating AI interpretation..."):
            st.session_state["aquaguard_ai_explanation"] = explain_risk(context)

    if st.session_state.get("aquaguard_ai_explanation"):
        st.markdown("### AI risk interpretation and mitigation priorities")
        st.write(st.session_state["aquaguard_ai_explanation"])
