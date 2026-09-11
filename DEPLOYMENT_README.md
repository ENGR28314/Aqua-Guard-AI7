# AquaGuard AI Integrated Assessment Build

This package integrates the AquaGuard AI Assessment Center into the existing
`Export Data` tab of the uploaded app.py.

## Repository files

Keep these files together:

- app.py
- environment.py  <-- your existing AquaGuard AI environment module
- assessment_engine.py
- assessment_ui.py
- requirements.txt

The uploaded app already imports `environment.py`, so this package does not
replace your existing environment.py.

## New Export Data workflow

The Export Data tab now provides:

1. Download Project Screening CSV
2. Download Hazard Screening CSV
3. Upload one or more CSV files
4. Select/auto-detect the hazard for each dataset
5. Preview uploaded data
6. Run AquaGuard AI Assessment
7. Calculate descriptive statistics and screening proxies
8. Show multi-hazard comparison
9. Show a map when latitude/longitude columns exist
10. Download assessment and hazard-assessment CSV files

## Supported datasets

Water, wildfire, landslide, urban flooding, river/flash flooding,
drought/water stress, extreme heat, coastal flooding/sea level,
storm/cyclone, and general project data.

## Streamlit Cloud

Commit all four application modules to the same repository and ensure
`requirements.txt` contains the required packages.

Do not upload API keys into source code. If your existing environment.py
uses secrets, keep them in Streamlit Secrets.

## Important

The CSV assessment values are transparent screening proxies. They are not
official CHRI, government, World Bank, regulatory, or engineering design
values. Calibrate hazard-specific thresholds and indicator directions with
validated datasets before formal decisions.
