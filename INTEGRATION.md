# AquaGuard AI — Export Data + CSV Assessment Integration

## Files

Add these two files to the root of your Streamlit repository:

- `assessment_engine.py`
- `assessment_ui.py`

## requirements.txt

Make sure your project has:

```text
streamlit>=1.38
pandas>=2.0
numpy>=1.24
plotly>=5.20
```

## Add the import

Near the imports in `app.py`:

```python
from assessment_ui import render_assessment_center
```

## Put the upload + assessment controls inside Export Data

Your existing Export Data tab should contain something like:

```python
with tabs[EXPORT_DATA_TAB_INDEX]:

    st.subheader("Export Project Data")

    # Keep your existing project/hazard download buttons here.

    st.markdown("---")

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
```

IMPORTANT: If your existing variables use different names, replace them with
the variable names already present in your app.py.

## What the new section does

1. Upload one or many CSV files.
2. Select or auto-detect the hazard.
3. Preview the data.
4. Click `Run AquaGuard AI Assessment`.
5. Calculate:
   - row/column counts
   - numeric indicators
   - missing values
   - descriptive statistics
   - min/max/mean/std/percentiles
   - context-adjusted screening proxy
   - hazard-by-hazard comparison
6. Show a map when latitude/longitude columns exist.
7. Download assessment results as CSV.

## Supported hazards

- Water
- Wildfire
- Landslide
- Urban flooding
- River / flash flooding
- Drought / water stress
- Extreme heat
- Coastal flooding / sea level
- Storm / cyclone
- General project data

## Suggested CSV structure

Water:

```csv
latitude,longitude,date,ph,turbidity,water_level,temperature,dissolved_oxygen
31.5204,74.3587,2026-01-01,7.2,3.5,2.4,22.5,7.1
```

Wildfire:

```csv
latitude,longitude,date,temperature,humidity,wind_speed,fuel_moisture,fire_risk
34.15,73.20,2026-06-01,34,28,22,18,72
```

Landslide:

```csv
latitude,longitude,date,rainfall,slope,elevation,soil_moisture,landslide_probability
34.05,73.15,2026-07-01,82,38,1800,72,0.64
```

Urban flooding:

```csv
latitude,longitude,date,rainfall,drainage_capacity,water_level,flood_depth
31.5204,74.3587,2026-08-01,74,42,68,0.45
```

## Architecture

```text
Existing AquaGuard AI
        |
        +--> Export Data
                |
                +--> Existing downloads
                |
                +--> CSV Upload
                        |
                        v
                 Data validation
                        |
                        v
                 Statistics engine
                        |
                        +--> Data quality
                        +--> Descriptive statistics
                        +--> Hazard screening
                        +--> Climate context
                        +--> Scenario/horizon adjustment
                        +--> Multi-hazard results
                        |
                        v
                 Assessment dashboard
                        |
                        +--> Charts
                        +--> Map
                        +--> Download results
```

The assessment module is independent of the rest of AquaGuard AI. This makes
it easier to extend later with real Pakistan climate/hazard datasets or
specialized models.
