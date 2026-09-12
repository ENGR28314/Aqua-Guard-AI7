"""Idempotent patcher for the existing AquaGuard AI7 app.py.

Run from the repository root:
    python app_patch.py

It does NOT replace the existing application. It adds one import, one tab, and
one rendering call for the PostGIS/Global City/AI integration.
"""
from pathlib import Path

APP = Path("app.py")
MARKER = "# === AQUAGUARD POSTGIS GEOAI INTEGRATION ==="
IMPORT = "from geoai_ui import render_geoai_panel\n"
TAB = '    "🌐 PostGIS + GeoAI",\n'
BLOCK = f'''\n{MARKER}\nwith tabs[9]:\n    render_geoai_panel(\n        country=country,\n        country_iso3=COUNTRY_ISO3.get(country, ""),\n        project_name=project_name,\n        climate_division=climate_division,\n        scenario=scenario,\n        horizon=horizon,\n        exposure=exposure,\n        vulnerability=vulnerability,\n        adaptive_capacity=adaptive_capacity,\n        sensitivity=sensitivity,\n        criticality=criticality,\n    )\n'''

text = APP.read_text(encoding="utf-8")
if MARKER in text:
    print("AquaGuard PostGIS integration is already patched.")
    raise SystemExit(0)

if IMPORT not in text:
    needle = "from assessment_ui import render_assessment_center\n"
    if needle not in text:
        raise SystemExit("Could not find assessment_ui import in app.py")
    text = text.replace(needle, needle + IMPORT, 1)

needle = '    "💾 Export Data",\n])'
if needle not in text:
    raise SystemExit("Could not find AquaGuard tab list in app.py")
text = text.replace(needle, '    "💾 Export Data",\n' + TAB + '])', 1)

text += BLOCK
APP.write_text(text, encoding="utf-8")
print("Patched app.py without replacing existing functionality.")
