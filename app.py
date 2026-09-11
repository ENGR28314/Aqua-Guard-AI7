import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import the environment module as a single module so this app is resilient
# if an older environment.py is accidentally left in the GitHub repository.
import environment as env

# AquaGuard AI Assessment Center: CSV upload + project statistics
from assessment_ui import render_assessment_center

WORLD_COUNTRIES = env.WORLD_COUNTRIES
COUNTRY_ISO3 = env.COUNTRY_ISO3
CLIMATE_DIVISIONS = env.CLIMATE_DIVISIONS
HAZARDS = env.HAZARDS
SECTORS = env.SECTORS
SCENARIOS = env.SCENARIOS
calculate_risk = env.calculate_risk
calculate_chri_proxy = env.calculate_chri_proxy
calculate_ghg = env.calculate_ghg
calculate_hazard_scores = env.calculate_hazard_scores
build_dynamic_plan = env.build_dynamic_plan
climate_simulation_profile = env.climate_simulation_profile

st.set_page_config(
    page_title="AquaGuard AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Helpers ----------
def hazard_band(score):
    if score >= 70:
        return "High"
    if score >= 40:
        return "Moderate"
    return "Low"


def dynamic_hazard_scores(
    base_df,
    selected_hazards,
    hazard_multipliers,
    extra_pressure,
    priority_threshold,
):
    df = base_df.copy()

    # Apply user-selected hazard importance.
    df["Adjusted score"] = (
        df["Score"]
        * df["Hazard"].map(hazard_multipliers).fillna(1.0)
        + extra_pressure
    ).clip(0, 100)

    df["Dynamic priority"] = df["Adjusted score"].apply(hazard_band)

    # User-selected threshold can override the displayed priority.
    df["Action required"] = df["Adjusted score"] >= priority_threshold

    return df


# ---------- Sector engine compatibility layer ----------
# The previous deployment error happened because app.py referenced
# calculate_sector_profile while Streamlit was loading an older environment.py.
# This local fallback keeps the UI executable even if that older file is present.
SECTOR_HAZARD_WEIGHTS = getattr(env, "SECTOR_HAZARD_WEIGHTS", {
    "Agriculture": {"Extreme heat": .22, "Drought": .22, "Extreme precipitation": .16, "Flood": .16, "Storm": .08, "Wildfire": .08, "Landslide": .05, "Sea-level rise": .03},
    "Water": {"Drought": .24, "Flood": .22, "Extreme precipitation": .20, "Sea-level rise": .12, "Extreme heat": .10, "Storm": .07, "Landslide": .03, "Wildfire": .02},
    "Health": {"Extreme heat": .28, "Flood": .15, "Drought": .13, "Wildfire": .12, "Storm": .11, "Extreme precipitation": .10, "Sea-level rise": .06, "Landslide": .05},
    "Transportation": {"Flood": .20, "Extreme precipitation": .20, "Storm": .18, "Landslide": .15, "Extreme heat": .10, "Wildfire": .08, "Sea-level rise": .06, "Drought": .03},
    "Energy": {"Extreme heat": .20, "Storm": .19, "Flood": .18, "Drought": .15, "Wildfire": .10, "Sea-level rise": .08, "Extreme precipitation": .07, "Landslide": .03},
})

SECTOR_RISK_WEIGHTS = getattr(env, "SECTOR_RISK_WEIGHTS", {
    "Agriculture": {"exposure": .24, "vulnerability": .25, "adaptive": .14, "sensitivity": .22, "criticality": .15},
    "Water": {"exposure": .25, "vulnerability": .22, "adaptive": .13, "sensitivity": .20, "criticality": .20},
    "Health": {"exposure": .20, "vulnerability": .28, "adaptive": .15, "sensitivity": .25, "criticality": .12},
    "Transportation": {"exposure": .27, "vulnerability": .18, "adaptive": .15, "sensitivity": .18, "criticality": .22},
    "Energy": {"exposure": .25, "vulnerability": .18, "adaptive": .17, "sensitivity": .20, "criticality": .20},
})


def calculate_sector_profile(
    sector, country, climate_division, scenario, horizon,
    exposure, vulnerability, adaptive_capacity, sensitivity, criticality
):
    """Always-available dynamic sector calculator used by the UI."""
    if sector not in SECTORS:
        raise ValueError(f"Unknown sector: {sector}")

    climate = climate_simulation_profile(
        country, climate_division, scenario, horizon,
        exposure, vulnerability, adaptive_capacity, sensitivity, criticality,
    )

    rw = SECTOR_RISK_WEIGHTS[sector]
    project_pressure = (
        exposure * rw["exposure"]
        + vulnerability * rw["vulnerability"]
        + (100 - adaptive_capacity) * rw["adaptive"]
        + sensitivity * rw["sensitivity"]
        + criticality * rw["criticality"]
    )

    hw = SECTOR_HAZARD_WEIGHTS[sector]
    hazard_contributions = {
        h: climate["hazards"].get(h, 0) * w for h, w in hw.items()
    }
    climate_pressure = sum(hazard_contributions.values())

    sector_factor = {
        "Agriculture": 1.04,
        "Water": 1.06,
        "Health": 1.02,
        "Transportation": 0.98,
        "Energy": 1.00,
    }[sector]

    stress = max(0, min(100, (
        0.52 * project_pressure + 0.48 * climate_pressure
    ) * sector_factor))

    resilience = max(0, min(100,
        0.72 * adaptive_capacity + 0.28 * (100 - stress)
    ))
    risk_gap = max(0, min(100, stress - resilience + 50))
    priority = "High" if stress >= 70 else "Moderate" if stress >= 40 else "Low"

    top_driver, top_contribution = max(
        hazard_contributions.items(), key=lambda item: item[1]
    )

    return {
        "sector": sector,
        "country": country,
        "climate_division": climate_division,
        "scenario": scenario,
        "horizon": horizon,
        "climate_stress": round(stress, 1),
        "existing_resilience": round(resilience, 1),
        "risk_gap": round(risk_gap, 1),
        "priority": priority,
        "project_pressure": round(project_pressure, 1),
        "climate_pressure": round(climate_pressure, 1),
        "top_driver": top_driver,
        "top_driver_score": round(climate["hazards"].get(top_driver, 0), 1),
        "hazard_contributions": {
            k: round(v, 2) for k, v in hazard_contributions.items()
        },
    }


# ---------- Sidebar ----------
with st.sidebar:
    st.header("Project Setup")

    project_name = st.text_input(
        "Project name",
        "Climate-Resilient Development Project",
    )

    country = st.selectbox(
        "Country",
        WORLD_COUNTRIES,
        index=WORLD_COUNTRIES.index("Pakistan"),
    )

    climate_division = st.selectbox(
        "Climate division",
        CLIMATE_DIVISIONS,
        index=2,
    )

    scenario = st.selectbox(
        "Climate scenario",
        list(SCENARIOS.keys()),
        index=1,
    )

    horizon = st.selectbox(
        "Scenario horizon",
        ["Near term", "Mid century", "Long term"],
    )

    st.divider()
    st.header("Risk Inputs")

    exposure = st.slider("Exposure", 0, 100, 60)
    vulnerability = st.slider("Population vulnerability", 0, 100, 55)
    adaptive_capacity = st.slider("Adaptive capacity", 0, 100, 50)
    sensitivity = st.slider("Sensitivity", 0, 100, 55)
    criticality = st.slider("Asset/service criticality", 0, 100, 65)

risk_score, risk_level = calculate_risk(
    exposure,
    vulnerability,
    adaptive_capacity,
    sensitivity,
    criticality,
)

chri_proxy = calculate_chri_proxy(
    exposure,
    vulnerability,
    adaptive_capacity,
)

# ---------- Header ----------
st.title("🌍 AquaGuard AI")
st.caption("Interactive Climate, Environmental & Disaster-Risk Decision Support")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Selected country", country)
c2.metric("Project risk", f"{risk_score:.1f}/100", risk_level)
c3.metric("CHRI project proxy", f"{chri_proxy:.1f}/100")
c4.metric("Climate division", climate_division)

st.info(
    "Interactive engine: hazard scores, priorities, charts and action flags "
    "recalculate whenever you change project inputs or hazard controls."
)

tabs = st.tabs([
    "🌎 World Map",
    "📊 Risk Analytics",
    "🌡 Climate",
    "🏥 CHRI Proxy",
    "🏭 GHG & Carbon",
    "🌾 Sector Screening",
    "⚠️ Interactive Hazard Screening",
    "🛠 Dynamic Mitigation Plan",
    "💾 Export Data",
])

# ---------- World Map ----------
with tabs[0]:
    st.subheader("Interactive World Map")

    map_df = pd.DataFrame(COUNTRY_ISO3, columns=["country", "iso_alpha"])
    map_df["risk_score"] = 50.0
    map_df["status"] = "Placeholder — connect country dataset"

    selected = map_df["country"].eq(country)
    map_df.loc[selected, "risk_score"] = risk_score
    map_df.loc[selected, "status"] = f"Live project screening: {risk_level}"

    fig = px.choropleth(
        map_df,
        locations="iso_alpha",
        locationmode="ISO-3",
        color="risk_score",
        hover_name="country",
        hover_data={"risk_score": ":.1f", "status": True, "iso_alpha": False},
        color_continuous_scale="RdYlGn_r",
        range_color=(0, 100),
        projection="natural earth",
        title="AquaGuard AI — Global Screening Map",
    )
    fig.update_geos(
        showcountries=True,
        showcoastlines=True,
        showland=True,
    )
    fig.update_layout(height=600, margin=dict(l=0, r=0, t=55, b=0))
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"scrollZoom": True, "displaylogo": False, "responsive": True},
    )

# ---------- Risk Analytics ----------
with tabs[1]:
    st.subheader("Interactive Risk Analytics")

    risk_df = pd.DataFrame({
        "Indicator": [
            "Exposure", "Vulnerability", "Sensitivity",
            "Criticality", "Adaptive capacity"
        ],
        "Score": [
            exposure, vulnerability, sensitivity,
            criticality, adaptive_capacity
        ],
    })

    fig = px.bar(
        risk_df,
        x="Indicator",
        y="Score",
        range_y=[0, 100],
        text="Score",
        title="Current Project Risk Drivers",
    )
    st.plotly_chart(fig, use_container_width=True)

    radar = px.line_polar(
        risk_df,
        r="Score",
        theta="Indicator",
        line_close=True,
        range_r=[0, 100],
        title="Current Risk Profile",
    )
    radar.update_traces(fill="toself")
    st.plotly_chart(radar, use_container_width=True)

# ---------- Climate ----------
with tabs[2]:
    st.subheader("🌡 Dynamic Climate Scenario Simulator")

    st.markdown(
        "This simulator is fully linked to the selected **country**, "
        "**climate division**, **Low/Moderate/High scenario**, **time horizon**, "
        "and all five project-risk inputs. Changing any of them recalculates "
        "the climate pathway, climate stress, hazard response and scenario comparison."
    )

    climate_profile = climate_simulation_profile(
        country=country,
        climate_division=climate_division,
        scenario=scenario,
        horizon=horizon,
        exposure=exposure,
        vulnerability=vulnerability,
        adaptive_capacity=adaptive_capacity,
        sensitivity=sensitivity,
        criticality=criticality,
    )

    # ---- Live summary ----
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Country", country)
    c2.metric("Climate division", climate_division)
    c3.metric(
        "Temperature change",
        f'{climate_profile["temperature_change"]:+.2f} °C',
    )
    c4.metric(
        "Precipitation change",
        f'{climate_profile["precipitation_change"]:+.1f}%',
    )

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Scenario", scenario)
    c6.metric("Horizon", horizon)
    c7.metric(
        "Dynamic climate pressure",
        f'{climate_profile["risk_pressure"]:.1f}/100',
    )
    c8.metric(
        "Project response multiplier",
        f'{climate_profile["project_multiplier"]:.2f}×',
    )

    st.info(
        "Screening model only: the country and climate-division modifiers are "
        "transparent planning factors, not observed climate projections. "
        "For formal decisions, connect validated climate datasets."
    )

    # ---- Dynamic pathway controls ----
    st.markdown("### 1. Dynamic pathway")

    pathway_mode = st.radio(
        "Pathway view",
        ["Selected scenario", "Compare all scenarios"],
        horizontal=True,
        key="climate_pathway_mode",
    )

    years = list(range(2025, 2101, 5))
    target_years = {
        "Near term": 2040,
        "Mid century": 2050,
        "Long term": 2080,
    }

    def build_pathway(profile):
        target_year = target_years[profile["horizon"]]
        rows = []

        for year in years:
            if year <= target_year:
                progress = (year - 2025) / max(1, target_year - 2025)
            else:
                # Continue the selected pathway beyond the horizon rather than
                # flattening or jumping back to zero.
                progress = 1.0 + 0.35 * (
                    (year - target_year) / max(1, 2100 - target_year)
                )

            rows.append({
                "Year": year,
                "Temperature change (°C)": profile["temperature_change"] * progress,
                "Precipitation change (%)": profile["precipitation_change"] * progress,
            })

        return pd.DataFrame(rows)

    selected_pathway_df = build_pathway(climate_profile)

    if pathway_mode == "Selected scenario":
        st.markdown(
            f"**{country} · {climate_division} · {scenario} · {horizon}**"
        )

        # Separate charts prevent temperature and precipitation from being
        # visually compressed onto one incompatible y-axis.
        temp_fig = px.line(
            selected_pathway_df,
            x="Year",
            y="Temperature change (°C)",
            markers=True,
            title="Dynamic temperature pathway",
        )
        temp_fig.add_hline(y=0, line_dash="dot")
        temp_fig.update_layout(height=390)
        st.plotly_chart(
            temp_fig,
            use_container_width=True,
            config={"displaylogo": False, "scrollZoom": True},
        )

        precip_fig = px.line(
            selected_pathway_df,
            x="Year",
            y="Precipitation change (%)",
            markers=True,
            title="Dynamic precipitation pathway",
        )
        precip_fig.add_hline(y=0, line_dash="dot")
        precip_fig.update_layout(height=390)
        st.plotly_chart(
            precip_fig,
            use_container_width=True,
            config={"displaylogo": False, "scrollZoom": True},
        )
    else:
        comparison_rows = []
        for s_name in SCENARIOS:
            p = climate_simulation_profile(
                country, climate_division, s_name, horizon,
                exposure, vulnerability, adaptive_capacity,
                sensitivity, criticality,
            )
            for year in years:
                target_year = target_years[horizon]
                if year <= target_year:
                    progress = (year - 2025) / max(1, target_year - 2025)
                else:
                    progress = 1.0 + 0.35 * (
                        (year - target_year) / max(1, 2100 - target_year)
                    )

                comparison_rows.append({
                    "Year": year,
                    "Scenario": s_name,
                    "Temperature change (°C)": p["temperature_change"] * progress,
                    "Precipitation change (%)": p["precipitation_change"] * progress,
                })

        comparison_df = pd.DataFrame(comparison_rows)

        st.plotly_chart(
            px.line(
                comparison_df,
                x="Year",
                y="Temperature change (°C)",
                color="Scenario",
                markers=True,
                title=f"Temperature pathways — {country} / {climate_division}",
            ),
            use_container_width=True,
        )

        st.plotly_chart(
            px.line(
                comparison_df,
                x="Year",
                y="Precipitation change (%)",
                color="Scenario",
                markers=True,
                title=f"Precipitation pathways — {country} / {climate_division}",
            ),
            use_container_width=True,
        )

    # ---- Risk-input response matrix ----
    st.markdown("### 2. Risk-input sensitivity")

    risk_inputs = {
        "Exposure": exposure,
        "Population vulnerability": vulnerability,
        "Adaptive capacity": adaptive_capacity,
        "Sensitivity": sensitivity,
        "Asset/service criticality": criticality,
    }

    sensitivity_rows = []
    for name, value in risk_inputs.items():
        test_values = [max(0, value - 20), value, min(100, value + 20)]
        for test_value in test_values:
            kwargs = {
                "country": country,
                "climate_division": climate_division,
                "scenario": scenario,
                "horizon": horizon,
                "exposure": exposure,
                "vulnerability": vulnerability,
                "adaptive_capacity": adaptive_capacity,
                "sensitivity": sensitivity,
                "criticality": criticality,
            }
            if name == "Exposure":
                kwargs["exposure"] = test_value
            elif name == "Population vulnerability":
                kwargs["vulnerability"] = test_value
            elif name == "Adaptive capacity":
                kwargs["adaptive_capacity"] = test_value
            elif name == "Sensitivity":
                kwargs["sensitivity"] = test_value
            else:
                kwargs["criticality"] = test_value

            p = climate_simulation_profile(**kwargs)
            sensitivity_rows.append({
                "Risk input": name,
                "Input value": test_value,
                "Temperature change (°C)": p["temperature_change"],
                "Precipitation change (%)": p["precipitation_change"],
                "Climate pressure": p["risk_pressure"],
            })

    sensitivity_df = pd.DataFrame(sensitivity_rows)

    st.plotly_chart(
        px.line(
            sensitivity_df,
            x="Input value",
            y="Climate pressure",
            color="Risk input",
            markers=True,
            title="How each risk input changes climate pressure",
        ),
        use_container_width=True,
    )

    # ---- Climate hazard response ----
    st.markdown("### 3. Dynamic climate-hazard response")

    hazard_response = pd.DataFrame([
        {"Hazard": h, "Dynamic pressure": v}
        for h, v in climate_profile["hazards"].items()
    ]).sort_values("Dynamic pressure", ascending=True)

    hazard_fig = px.bar(
        hazard_response,
        x="Dynamic pressure",
        y="Hazard",
        orientation="h",
        text="Dynamic pressure",
        range_x=[0, 100],
        color="Dynamic pressure",
        title="Climate-sensitive hazard pressure",
    )
    hazard_fig.update_layout(height=500)
    st.plotly_chart(
        hazard_fig,
        use_container_width=True,
        config={"displaylogo": False, "scrollZoom": True},
    )

    # ---- Scenario matrix ----
    st.markdown("### 4. Scenario × risk-input response")

    scenario_rows = []
    for s_name in SCENARIOS:
        p = climate_simulation_profile(
            country, climate_division, s_name, horizon,
            exposure, vulnerability, adaptive_capacity,
            sensitivity, criticality,
        )
        scenario_rows.append({
            "Scenario": s_name,
            "Temperature change (°C)": p["temperature_change"],
            "Precipitation change (%)": p["precipitation_change"],
            "Dynamic climate pressure": p["risk_pressure"],
            "Response multiplier": p["project_multiplier"],
        })

    scenario_df = pd.DataFrame(scenario_rows)

    st.dataframe(
        scenario_df.round(2),
        use_container_width=True,
        hide_index=True,
    )

    st.plotly_chart(
        px.scatter(
            scenario_df,
            x="Temperature change (°C)",
            y="Precipitation change (%)",
            size="Dynamic climate pressure",
            color="Scenario",
            text="Scenario",
            hover_data=["Dynamic climate pressure", "Response multiplier"],
            title="Scenario response under the current country, division and risk inputs",
        ),
        use_container_width=True,
    )

    # ---- Current driver cards ----
    st.markdown("### 5. Current project drivers")

    driver_df = pd.DataFrame({
        "Risk input": list(risk_inputs.keys()),
        "Current value": list(risk_inputs.values()),
    })

    st.plotly_chart(
        px.bar(
            driver_df,
            x="Risk input",
            y="Current value",
            text="Current value",
            range_y=[0, 100],
            title="Current inputs feeding the climate simulator",
        ),
        use_container_width=True,
    )

    # Export both selected pathway and summary.
    export_df = selected_pathway_df.copy()
    export_df["Country"] = country
    export_df["Climate division"] = climate_division
    export_df["Scenario"] = scenario
    export_df["Horizon"] = horizon
    export_df["Exposure"] = exposure
    export_df["Population vulnerability"] = vulnerability
    export_df["Adaptive capacity"] = adaptive_capacity
    export_df["Sensitivity"] = sensitivity
    export_df["Asset/service criticality"] = criticality
    export_df["Dynamic climate pressure"] = climate_profile["risk_pressure"]

    st.download_button(
        "⬇️ Download dynamic climate simulation CSV",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name="aquaguard_dynamic_climate_simulation_v4.csv",
        mime="text/csv",
    )

# ---------- CHRI ----------
with tabs[3]:
    st.subheader("Climate Health Risk — Project Proxy")
    a, b, c = st.columns(3)
    a.metric("Hazard pressure", f"{exposure}/100")
    b.metric("Population vulnerability", f"{vulnerability}/100")
    c.metric("Health-system readiness", f"{adaptive_capacity}/100")
    st.metric("Illustrative CHRI proxy", f"{chri_proxy:.1f}/100")
    st.warning("This is an illustrative project proxy, not the official World Bank CHRI.")

# ---------- GHG ----------
with tabs[4]:
    st.subheader("GHG & Carbon Calculator")

    a, b, c = st.columns(3)
    electricity = a.number_input("Electricity (MWh/year)", min_value=0.0, value=1000.0, step=100.0)
    fuel = b.number_input("Liquid fuel (litres/year)", min_value=0.0, value=50000.0, step=5000.0)
    travel = c.number_input("Vehicle travel (km/year)", min_value=0.0, value=200000.0, step=10000.0)
    lifetime = st.slider("Project lifetime (years)", 1, 100, 25)

    ghg = calculate_ghg(electricity, fuel, travel, lifetime)

    a, b = st.columns(2)
    a.metric("Annual GHG", f'{ghg["annual_tco2e"]:.2f} tCO₂e')
    b.metric("Lifetime GHG", f'{ghg["lifetime_tco2e"]:.2f} tCO₂e')

    ghg_df = pd.DataFrame({
        "Source": ["Electricity", "Liquid fuel", "Vehicle travel"],
        "tCO₂e/year": [
            ghg["electricity_tco2e"],
            ghg["fuel_tco2e"],
            ghg["travel_tco2e"],
        ],
    })
    st.plotly_chart(
        px.pie(ghg_df, names="Source", values="tCO₂e/year", title="Annual GHG Contribution"),
        use_container_width=True,
    )

# ---------- Sector ----------
with tabs[5]:
    st.subheader("🏭 Interactive Sector Screening")

    st.markdown(
        "Sector performance is recalculated from the selected **country**, "
        "**climate division**, **scenario**, **horizon**, and all five project-risk inputs. "
        "No sector score is hard-coded."
    )

    selected_sector = st.selectbox(
        "Inspect a sector",
        SECTORS,
        key="sector_main",
    )

    selected_profile = calculate_sector_profile(
        selected_sector,
        country,
        climate_division,
        scenario,
        horizon,
        exposure,
        vulnerability,
        adaptive_capacity,
        sensitivity,
        criticality,
    )

    # ---- Live selected-sector dashboard ----
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(
        f"{selected_sector} climate stress",
        f'{selected_profile["climate_stress"]:.1f}/100',
    )
    m2.metric(
        "Existing resilience",
        f'{selected_profile["existing_resilience"]:.1f}/100',
    )
    m3.metric(
        "Risk gap",
        f'{selected_profile["risk_gap"]:.1f}/100',
    )
    m4.metric(
        "Top climate driver",
        selected_profile["top_driver"],
        f'{selected_profile["top_driver_score"]:.1f}/100',
    )

    st.caption(
        f'{country} · {climate_division} · {scenario} · {horizon} · '
        f'Priority: {selected_profile["priority"]}'
    )

    # ---- Sector comparison ----
    st.markdown("### 1. Live sector comparison")

    sector_rows = []
    for sec in SECTORS:
        p = calculate_sector_profile(
            sec,
            country,
            climate_division,
            scenario,
            horizon,
            exposure,
            vulnerability,
            adaptive_capacity,
            sensitivity,
            criticality,
        )
        sector_rows.append({
            "Sector": sec,
            "Climate stress": p["climate_stress"],
            "Existing resilience": p["existing_resilience"],
            "Risk gap": p["risk_gap"],
            "Priority": p["priority"],
            "Top climate driver": p["top_driver"],
        })

    sector_df = pd.DataFrame(sector_rows)

    fig_sector = px.bar(
        sector_df,
        x="Sector",
        y=["Climate stress", "Existing resilience"],
        barmode="group",
        range_y=[0, 100],
        title="Live Sector Climate Stress vs Existing Resilience",
        hover_data=["Risk gap", "Priority", "Top climate driver"],
    )
    st.plotly_chart(
        fig_sector,
        use_container_width=True,
        config={"displaylogo": False, "scrollZoom": True},
    )

    st.dataframe(
        sector_df.round(1),
        use_container_width=True,
        hide_index=True,
    )

    # ---- Selected sector climate drivers ----
    st.markdown("### 2. Selected-sector climate drivers")

    driver_df = pd.DataFrame([
        {"Hazard": h, "Contribution": v}
        for h, v in selected_profile["hazard_contributions"].items()
    ]).sort_values("Contribution", ascending=True)

    fig_driver = px.bar(
        driver_df,
        x="Contribution",
        y="Hazard",
        orientation="h",
        text="Contribution",
        title=f"Climate drivers affecting {selected_sector}",
    )
    st.plotly_chart(
        fig_driver,
        use_container_width=True,
        config={"displaylogo": False, "scrollZoom": True},
    )

    # ---- Project input influence ----
    st.markdown("### 3. Risk-input response")

    risk_values = {
        "Exposure": exposure,
        "Population vulnerability": vulnerability,
        "Adaptive capacity": adaptive_capacity,
        "Sensitivity": sensitivity,
        "Asset/service criticality": criticality,
    }

    sensitivity_rows = []
    for name, value in risk_values.items():
        for test_value in sorted(set([
            max(0, value - 20),
            value,
            min(100, value + 20),
        ])):
            kwargs = {
                "sector": selected_sector,
                "country": country,
                "climate_division": climate_division,
                "scenario": scenario,
                "horizon": horizon,
                "exposure": exposure,
                "vulnerability": vulnerability,
                "adaptive_capacity": adaptive_capacity,
                "sensitivity": sensitivity,
                "criticality": criticality,
            }

            if name == "Exposure":
                kwargs["exposure"] = test_value
            elif name == "Population vulnerability":
                kwargs["vulnerability"] = test_value
            elif name == "Adaptive capacity":
                kwargs["adaptive_capacity"] = test_value
            elif name == "Sensitivity":
                kwargs["sensitivity"] = test_value
            else:
                kwargs["criticality"] = test_value

            p = calculate_sector_profile(**kwargs)
            sensitivity_rows.append({
                "Risk input": name,
                "Input value": test_value,
                "Sector stress": p["climate_stress"],
                "Resilience": p["existing_resilience"],
            })

    sensitivity_df = pd.DataFrame(sensitivity_rows)

    st.plotly_chart(
        px.line(
            sensitivity_df,
            x="Input value",
            y="Sector stress",
            color="Risk input",
            markers=True,
            title=f"How each risk input changes {selected_sector} stress",
        ),
        use_container_width=True,
    )

    # ---- Scenario and horizon matrix ----
    st.markdown("### 4. Scenario × horizon response")

    matrix_rows = []
    for s_name in ["Low", "Moderate", "High"]:
        for h_name in ["Near term", "Mid century", "Long term"]:
            p = calculate_sector_profile(
                selected_sector,
                country,
                climate_division,
                s_name,
                h_name,
                exposure,
                vulnerability,
                adaptive_capacity,
                sensitivity,
                criticality,
            )
            matrix_rows.append({
                "Scenario": s_name,
                "Horizon": h_name,
                "Climate stress": p["climate_stress"],
                "Resilience": p["existing_resilience"],
                "Risk gap": p["risk_gap"],
                "Top driver": p["top_driver"],
            })

    matrix_df = pd.DataFrame(matrix_rows)

    st.plotly_chart(
        px.line(
            matrix_df,
            x="Horizon",
            y="Climate stress",
            color="Scenario",
            markers=True,
            category_orders={
                "Horizon": ["Near term", "Mid century", "Long term"]
            },
            title=f"{selected_sector}: scenario and horizon response",
        ),
        use_container_width=True,
    )

    st.dataframe(
        matrix_df.round(1),
        use_container_width=True,
        hide_index=True,
    )

    # ---- Country/division comparison ----
    st.markdown("### 5. Current country & climate-division effect")

    st.write(
        "The selected country and climate division feed the climate engine, "
        "which changes the hazard mix used by this sector."
    )

    comparison_df = pd.DataFrame({
        "Driver": [
            "Project pressure",
            "Climate pressure",
            "Sector stress",
            "Existing resilience",
            "Risk gap",
        ],
        "Value": [
            selected_profile["project_pressure"],
            selected_profile["climate_pressure"],
            selected_profile["climate_stress"],
            selected_profile["existing_resilience"],
            selected_profile["risk_gap"],
        ],
    })

    st.plotly_chart(
        px.bar(
            comparison_df,
            x="Driver",
            y="Value",
            text="Value",
            range_y=[0, 100],
            title=f"{selected_sector} — current screening profile",
        ),
        use_container_width=True,
    )

    # ---- Export ----
    export_sector = sector_df.copy()
    export_sector["Country"] = country
    export_sector["Climate division"] = climate_division
    export_sector["Scenario"] = scenario
    export_sector["Horizon"] = horizon
    export_sector["Exposure"] = exposure
    export_sector["Population vulnerability"] = vulnerability
    export_sector["Adaptive capacity"] = adaptive_capacity
    export_sector["Sensitivity"] = sensitivity
    export_sector["Asset/service criticality"] = criticality

    st.download_button(
        "⬇️ Download sector screening CSV",
        data=export_sector.to_csv(index=False).encode("utf-8"),
        file_name="aquaguard_dynamic_sector_screening_v5.csv",
        mime="text/csv",
    )

# ---------- Interactive Hazard Screening ----------
with tabs[6]:
    st.subheader("⚠️ Interactive Hazard Screening")

    st.markdown(
        "Use the controls below to change how each hazard responds to the "
        "current project conditions. Every chart and table is recalculated "
        "from the current values."
    )

    base_hazards = calculate_hazard_scores(
        exposure=exposure,
        vulnerability=vulnerability,
        adaptive_capacity=adaptive_capacity,
        sensitivity=sensitivity,
        criticality=criticality,
        climate_division=climate_division,
        scenario=scenario,
        horizon=horizon,
    )

    # Scenario-driven default multiplier.
    scenario_default = {"Low": 0.90, "Moderate": 1.00, "High": 1.15}[scenario]
    horizon_default = {
        "Near term": 0.95,
        "Mid century": 1.00,
        "Long term": 1.10,
    }[horizon]

    st.markdown("### 1. Hazard controls")

    control_cols = st.columns(4)
    selected_hazards = st.multiselect(
        "Hazards included in the interactive assessment",
        HAZARDS,
        default=HAZARDS,
        key="hazard_selection",
    )

    # One slider per hazard. Multipliers are intentionally transparent.
    hazard_multipliers = {}
    for i, hazard in enumerate(HAZARDS):
        col = control_cols[i % 4]
        with col:
            hazard_multipliers[hazard] = st.slider(
                f"{hazard} importance",
                0.50,
                1.50,
                float(scenario_default),
                0.05,
                key=f"mult_{hazard}",
                help="1.00 = base calculated pressure. Higher values increase the hazard's planning priority.",
            )

    extra_pressure = st.slider(
        "Additional project-specific pressure applied to selected hazards",
        -20,
        20,
        0,
        1,
        help="Use this only when your project team has evidence for an additional local pressure adjustment.",
    )

    priority_threshold = st.slider(
        "Action-required threshold",
        30,
        90,
        60,
        5,
        help="Hazards at or above this score are flagged for action.",
    )

    # Dynamic calculation.
    dynamic_df = dynamic_hazard_scores(
        base_hazards,
        selected_hazards,
        hazard_multipliers,
        extra_pressure,
        priority_threshold,
    )

    dynamic_df["Selected"] = dynamic_df["Hazard"].isin(selected_hazards)

    # Add context columns used by the Plotly hover template.
    # These columns must exist in the dataframe passed to px.bar().
    dynamic_df["Climate division"] = climate_division
    dynamic_df["Scenario"] = scenario
    dynamic_df["Horizon"] = horizon

    # Only selected hazards are part of the active plan.
    active_df = dynamic_df[dynamic_df["Selected"]].copy()

    if active_df.empty:
        st.warning("Select at least one hazard to continue.")
    else:
        st.markdown("### 2. Live hazard dashboard")

        highest = active_df.loc[active_df["Adjusted score"].idxmax()]
        high_count = int((active_df["Adjusted score"] >= 70).sum())
        action_count = int(active_df["Action required"].sum())

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Active hazards", len(active_df))
        m2.metric("Highest hazard", highest["Hazard"], f'{highest["Adjusted score"]:.1f}/100')
        m3.metric("High-risk hazards", high_count)
        m4.metric("Actions required", action_count)

        # Interactive chart with rich hover information.
        chart_df = active_df.sort_values("Adjusted score", ascending=True)

        fig = px.bar(
            chart_df,
            x="Adjusted score",
            y="Hazard",
            orientation="h",
            color="Dynamic priority",
            text=chart_df["Adjusted score"].round(0),
            range_x=[0, 100],
            custom_data=[
                "Score",
                "Dynamic priority",
                "Action required",
                "Climate division",
                "Scenario",
                "Horizon",
            ],
            title="Live Hazard Pressure — recalculated from your inputs",
        )
        fig.update_traces(
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Adjusted score: %{x:.1f}<br>"
                "Base score: %{customdata[0]:.1f}<br>"
                "Priority: %{customdata[1]}<br>"
                "Action required: %{customdata[2]}<br>"
                "Climate division: %{customdata[3]}<br>"
                "Scenario: %{customdata[4]}<br>"
                "Horizon: %{customdata[5]}<extra></extra>"
            )
        )
        fig.update_layout(height=520)
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "responsive": True,
                "scrollZoom": True,
            },
        )

        st.markdown("### 3. Compare base pressure vs adjusted pressure")

        compare = active_df[["Hazard", "Score", "Adjusted score"]].copy()
        compare = compare.rename(columns={
            "Score": "Base score",
            "Adjusted score": "Adjusted score",
        })

        melted = compare.melt(
            id_vars="Hazard",
            value_vars=["Base score", "Adjusted score"],
            var_name="Measure",
            value_name="Score",
        )

        st.plotly_chart(
            px.bar(
                melted,
                x="Hazard",
                y="Score",
                color="Measure",
                barmode="group",
                range_y=[0, 100],
                title="Base vs Current User-Adjusted Hazard Score",
            ),
            use_container_width=True,
        )

        st.markdown("### 4. Dynamic hazard matrix")

        display_df = active_df[
            [
                "Hazard",
                "Score",
                "Adjusted score",
                "Dynamic priority",
                "Action required",
                "Climate division",
                "Scenario",
                "Horizon",
            ]
        ].copy()

        display_df["Score"] = display_df["Score"].round(1)
        display_df["Adjusted score"] = display_df["Adjusted score"].round(1)

        st.dataframe(
            display_df.sort_values("Adjusted score", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

        # Individual hazard drill-down.
        st.markdown("### 5. Hazard drill-down")

        drill_hazard = st.selectbox(
            "Choose a hazard for detailed analysis",
            active_df["Hazard"].tolist(),
            key="hazard_drilldown",
        )

        selected_row = active_df[active_df["Hazard"] == drill_hazard].iloc[0]
        drill_score = float(selected_row["Adjusted score"])

        d1, d2, d3, d4 = st.columns(4)
        d1.metric("Base pressure", f'{selected_row["Score"]:.1f}/100')
        d2.metric("Adjusted pressure", f'{drill_score:.1f}/100')
        d3.metric("Priority", selected_row["Dynamic priority"])
        d4.metric("Action required", "YES" if selected_row["Action required"] else "NO")

        # Show which project inputs are driving the overall hazard screening.
        driver_df = pd.DataFrame({
            "Project input": [
                "Exposure",
                "Vulnerability",
                "Sensitivity",
                "Criticality",
                "Adaptive capacity",
            ],
            "Current value": [
                exposure,
                vulnerability,
                sensitivity,
                criticality,
                adaptive_capacity,
            ],
        })

        st.plotly_chart(
            px.bar(
                driver_df,
                x="Project input",
                y="Current value",
                range_y=[0, 100],
                text="Current value",
                title=f"Project drivers for {drill_hazard}",
            ),
            use_container_width=True,
        )

        # Scenario/horizon effect for the selected hazard.
        scenario_rows = []
        for s_name in SCENARIOS:
            for h_name in ["Near term", "Mid century", "Long term"]:
                temp = calculate_hazard_scores(
                    exposure,
                    vulnerability,
                    adaptive_capacity,
                    sensitivity,
                    criticality,
                    climate_division,
                    s_name,
                    h_name,
                )
                row = temp[temp["Hazard"] == drill_hazard].iloc[0]
                adjusted = min(
                    100,
                    max(
                        0,
                        float(row["Score"])
                        * hazard_multipliers[drill_hazard]
                        + extra_pressure,
                    ),
                )
                scenario_rows.append({
                    "Scenario": s_name,
                    "Horizon": h_name,
                    "Score": adjusted,
                })

        scenario_df = pd.DataFrame(scenario_rows)

        st.plotly_chart(
            px.line(
                scenario_df,
                x="Horizon",
                y="Score",
                color="Scenario",
                markers=True,
                range_y=[0, 100],
                title=f"{drill_hazard} — dynamic scenario sensitivity",
            ),
            use_container_width=True,
        )

        st.download_button(
            "⬇️ Download current hazard assessment CSV",
            data=active_df.to_csv(index=False).encode("utf-8"),
            file_name="aquaguard_interactive_hazard_assessment.csv",
            mime="text/csv",
        )

# ---------- Dynamic Mitigation Plan ----------
with tabs[7]:
    st.subheader("🛠 Dynamic Mitigation & Adaptation Plan")

    hazard_df = calculate_hazard_scores(
        exposure,
        vulnerability,
        adaptive_capacity,
        sensitivity,
        criticality,
        climate_division,
        scenario,
        horizon,
    )

    # Make the mitigation plan use the same user-controlled hazard multipliers
    # as the hazard-screening tab, so the two tabs remain connected.
    hazard_multipliers = {
        h: st.session_state.get(f"mult_{h}", {"Low": 0.90, "Moderate": 1.00, "High": 1.15}[scenario])
        for h in HAZARDS
    }

    hazard_df["Score"] = (
        hazard_df["Score"]
        * hazard_df["Hazard"].map(hazard_multipliers)
    ).clip(0, 100)

    selected_hazards_plan = st.multiselect(
        "Hazards to include in the action plan",
        HAZARDS,
        default=[
            h for h in hazard_df.sort_values("Score", ascending=False)
            .head(5)["Hazard"]
        ],
        key="plan_hazards",
    )

    selected_sector_plan = st.selectbox(
        "Priority sector",
        SECTORS,
        key="mitigation_sector",
    )

    if selected_hazards_plan:
        plan_df = build_dynamic_plan(
            hazard_df=hazard_df,
            selected_hazards=selected_hazards_plan,
            sector=selected_sector_plan,
            climate_division=climate_division,
            scenario=scenario,
            horizon=horizon,
            adaptive_capacity=adaptive_capacity,
            vulnerability=vulnerability,
            sensitivity=sensitivity,
            criticality=criticality,
        )

        st.success(
            "The action plan is connected to the interactive hazard engine. "
            "Change risk inputs or hazard importance to regenerate priorities."
        )

        st.dataframe(
            plan_df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "⬇️ Download Dynamic Mitigation Plan CSV",
            data=plan_df.to_csv(index=False).encode("utf-8"),
            file_name="aquaguard_dynamic_mitigation_plan.csv",
            mime="text/csv",
        )
    else:
        st.warning("Select at least one hazard.")

# ---------- Export + AquaGuard AI Assessment Center ----------
with tabs[8]:
    st.subheader("Export Project Data")

    export_hazard_df = calculate_hazard_scores(
        exposure,
        vulnerability,
        adaptive_capacity,
        sensitivity,
        criticality,
        climate_division,
        scenario,
        horizon,
    )

    screening = pd.DataFrame([{
        "Project": project_name,
        "Country": country,
        "Climate division": climate_division,
        "Scenario": scenario,
        "Horizon": horizon,
        "Risk score": round(risk_score, 2),
        "Risk level": risk_level,
        "CHRI proxy": round(chri_proxy, 2),
        "Exposure": exposure,
        "Vulnerability": vulnerability,
        "Adaptive capacity": adaptive_capacity,
        "Sensitivity": sensitivity,
        "Criticality": criticality,
    }])

    st.dataframe(screening, use_container_width=True, hide_index=True)

    # Existing project exports.
    export_cols = st.columns(2)
    with export_cols[0]:
        st.download_button(
            "⬇️ Download Project Screening CSV",
            data=screening.to_csv(index=False).encode("utf-8"),
            file_name="aquaguard_project_screening.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with export_cols[1]:
        st.download_button(
            "⬇️ Download Hazard Screening CSV",
            data=export_hazard_df.to_csv(index=False).encode("utf-8"),
            file_name="aquaguard_hazard_screening.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("---")
    st.subheader("📊 AquaGuard AI Assessment Center")
    st.caption(
        "Upload one or more environmental/project CSV datasets and run "
        "statistics and transparent screening proxies using the current "
        "country, climate division, scenario and scenario horizon."
    )

    render_assessment_center(
        country=country,
        climate_division=climate_division,
        scenario=scenario,
        horizon=horizon,
        project_name=project_name,
        exposure=exposure,
        vulnerability=vulnerability,
        adaptive_capacity=adaptive_capacity,
        sensitivity=sensitivity,
        criticality=criticality,
    )

st.divider()
st.caption("AquaGuard AI • Interactive screening prototype")
