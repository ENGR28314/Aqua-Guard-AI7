
"""
AquaGuard AI Assessment Center UI.

Use in app.py:

    from assessment_ui import render_assessment_center

    with tabs[ASSESSMENT_TAB_INDEX]:
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

If you want the controls inside an existing Export Data tab, call the same
function from that tab.
"""

from __future__ import annotations

import io
import pandas as pd
import plotly.express as px
import streamlit as st

from assessment_engine import assess_dataset, build_project_statistics


HAZARD_OPTIONS = [
    "Auto-detect",
    "Water",
    "Wildfire",
    "Landslide",
    "Urban flooding",
    "River / flash flooding",
    "Drought / water stress",
    "Extreme heat",
    "Coastal flooding / sea level",
    "Storm / cyclone",
    "General project data",
]


def _download_csv(df: pd.DataFrame, filename: str, label: str):
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=label,
        data=csv,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


def render_assessment_center(
    country="Pakistan",
    climate_division="Temperate",
    scenario="Moderate",
    horizon="Near term",
    project_name="Climate-Resilient Development Project",
    exposure=60,
    vulnerability=55,
    adaptive_capacity=50,
    sensitivity=50,
    criticality=50,
):
    st.subheader("📊 AquaGuard AI Assessment Center")

    st.info(
        f"Assessment context: **{project_name}** · **{country}** · "
        f"**{climate_division}** · **{scenario} scenario** · **{horizon}**"
    )

    uploaded_files = st.file_uploader(
        "📤 Upload CSV files for AquaGuard AI Assessment",
        type=["csv"],
        accept_multiple_files=True,
        key="aquaguard_assessment_csv",
        help=(
            "Upload water, wildfire, landslide, urban flooding, flooding, "
            "drought, heat, coastal, storm or project datasets."
        ),
    )

    if not uploaded_files:
        st.caption(
            "You can upload multiple CSV files at once. "
            "The Run AquaGuard AI Assessment button will calculate "
            "dataset statistics and transparent screening proxies."
        )
        return

    st.success(f"{len(uploaded_files)} CSV file(s) ready for assessment.")

    results = []

    for i, uploaded in enumerate(uploaded_files):
        with st.expander(f"📄 {uploaded.name}", expanded=(i == 0)):
            try:
                df = pd.read_csv(io.BytesIO(uploaded.getvalue()))

                hazard = st.selectbox(
                    "Hazard type",
                    HAZARD_OPTIONS,
                    key=f"assessment_hazard_{i}",
                )

                st.dataframe(
                    df.head(15),
                    use_container_width=True,
                    hide_index=True,
                )

                st.caption(
                    f"{len(df):,} rows × {len(df.columns):,} columns"
                )

                if st.button(
                    "▶ Run AquaGuard AI Assessment",
                    key=f"run_single_assessment_{i}",
                    use_container_width=True,
                ):
                    st.session_state["aquaguard_run_assessment"] = True

                result = assess_dataset(
                    df=df,
                    filename=uploaded.name,
                    selected_hazard=hazard,
                    country=country,
                    climate_division=climate_division,
                    scenario=scenario,
                    horizon=horizon,
                )
                results.append(result)

            except Exception as exc:
                st.error(f"Unable to read {uploaded.name}: {exc}")

    st.markdown("---")

    if st.button(
        "▶ Run AquaGuard AI Assessment",
        type="primary",
        use_container_width=True,
        key="run_full_aquaguard_assessment",
    ):
        st.session_state["aquaguard_run_assessment"] = True

    if not st.session_state.get("aquaguard_run_assessment", False):
        st.info("Upload your datasets and click Run AquaGuard AI Assessment.")
        return

    if not results:
        st.warning("No valid CSV datasets are available.")
        return

    project = {
        "Project": project_name,
        "Country": country,
        "Climate division": climate_division,
        "Scenario": scenario,
        "Horizon": horizon,
        "Exposure": exposure,
        "Vulnerability": vulnerability,
        "Adaptive capacity": adaptive_capacity,
        "Sensitivity": sensitivity,
        "Criticality": criticality,
    }

    assessment = build_project_statistics(results, project)
    summary = assessment["summary"]

    st.markdown("## AquaGuard AI Assessment Results")

    a, b, c, d = st.columns(4)
    a.metric("Overall screening proxy", "—" if summary["overall_score"] is None else f'{summary["overall_score"]:.1f}/100')
    b.metric("Overall signal", summary["overall_level"])
    c.metric("Datasets assessed", summary["datasets"])
    d.metric("Total rows", f'{summary["rows"]:,}')

    st.markdown("### Project context")
    st.dataframe(
        pd.DataFrame(
            [{"Parameter": k, "Value": v} for k, v in project.items()]
        ),
        use_container_width=True,
        hide_index=True,
    )

    dataset_table = assessment["datasets"]
    if not dataset_table.empty:
        st.markdown("### Dataset statistics")
        st.dataframe(
            dataset_table,
            use_container_width=True,
            hide_index=True,
        )

        fig = px.bar(
            dataset_table,
            x="Hazard",
            y="Context-adjusted score",
            color="Signal",
            range_y=[0, 100],
            text="Context-adjusted score",
            title="AquaGuard AI multi-hazard screening profile",
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Hazard assessment")
        for result in results:
            st.markdown(
                f"#### {result['hazard']} — {result['filename']}"
            )

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Rows", f"{result['rows']:,}")
            m2.metric("Numeric indicators", result["numeric_count"])
            m3.metric("Missing", f"{result['missing_pct']:.1f}%")
            m4.metric(
                "Score",
                "—" if result["context_score"] is None else f"{result['context_score']:.1f}/100",
            )

            if result["stats"].empty:
                st.warning("No numeric indicators were found in this dataset.")
            else:
                st.dataframe(
                    result["stats"],
                    use_container_width=True,
                    hide_index=True,
                )

            with st.expander("Data quality"):
                st.dataframe(
                    result["missing"],
                    use_container_width=True,
                    hide_index=True,
                )

            if result.get("lat_column") and result.get("lon_column"):
                map_df = result["dataframe"][
                    [result["lat_column"], result["lon_column"]]
                ].copy()
                map_df.columns = ["lat", "lon"]
                map_df = map_df.dropna()
                if not map_df.empty:
                    st.map(map_df)

        st.markdown("### Export assessment results")
        _download_csv(
            dataset_table,
            "aquaguard_ai_assessment_results.csv",
            "📥 Download Assessment Results CSV",
        )

        hazard_table = summary["hazards"]
        if not hazard_table.empty:
            _download_csv(
                hazard_table,
                "aquaguard_ai_hazard_assessment.csv",
                "📥 Download Hazard Assessment CSV",
            )

        st.warning(
            "These scores are transparent prototype screening proxies. "
            "They are not official CHRI, regulatory, government, or "
            "World Bank assessments. Use validated hazard-specific "
            "thresholds, units, spatial methods and expert review before "
            "formal engineering or policy decisions."
        )
