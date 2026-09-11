import pandas as pd

CLIMATE_DIVISIONS = [
    "Tropical",
    "Dry / Arid",
    "Temperate",
    "Continental",
    "Polar",
    "Highland / Mountain"
]

HAZARDS = [
    "Flood",
    "Extreme heat",
    "Extreme precipitation",
    "Wildfire",
    "Drought",
    "Landslide",
    "Storm",
    "Sea-level rise"
]

SECTORS = [
    "Agriculture",
    "Water",
    "Health",
    "Transportation",
    "Energy"
]

# FIX FOR THE REPORTED NameError:
# app.py uses SECTOR_FACTORS[sector], so this registry must exist.
# The weights sum to 1.0 for every sector.
SECTOR_FACTORS = {
    "Agriculture": {
        "exposure_weight": 0.30,
        "vulnerability_weight": 0.30,
        "sensitivity_weight": 0.25,
        "adaptation_weight": 0.15
    },
    "Water": {
        "exposure_weight": 0.35,
        "vulnerability_weight": 0.25,
        "sensitivity_weight": 0.25,
        "adaptation_weight": 0.15
    },
    "Health": {
        "exposure_weight": 0.25,
        "vulnerability_weight": 0.35,
        "sensitivity_weight": 0.25,
        "adaptation_weight": 0.15
    },
    "Transportation": {
        "exposure_weight": 0.35,
        "vulnerability_weight": 0.20,
        "sensitivity_weight": 0.25,
        "adaptation_weight": 0.20
    },
    "Energy": {
        "exposure_weight": 0.30,
        "vulnerability_weight": 0.20,
        "sensitivity_weight": 0.25,
        "adaptation_weight": 0.25
    }
}

SCENARIOS = {
    "Low": {
        "Near term": {"temperature_delta": 0.4, "precipitation_pct": 2},
        "Mid century": {"temperature_delta": 1.0, "precipitation_pct": 4},
        "Long term": {"temperature_delta": 1.4, "precipitation_pct": 5}
    },
    "Moderate": {
        "Near term": {"temperature_delta": 0.6, "precipitation_pct": 3},
        "Mid century": {"temperature_delta": 1.8, "precipitation_pct": 6},
        "Long term": {"temperature_delta": 2.8, "precipitation_pct": 8}
    },
    "High": {
        "Near term": {"temperature_delta": 0.8, "precipitation_pct": 4},
        "Mid century": {"temperature_delta": 2.4, "precipitation_pct": 10},
        "Long term": {"temperature_delta": 4.2, "precipitation_pct": 15}
    }
}

# ISO-3 country list for Plotly's world geometry.
COUNTRY_ISO3 = [
    ("Afghanistan","AFG"),("Albania","ALB"),("Algeria","DZA"),("Andorra","AND"),
    ("Angola","AGO"),("Antigua and Barbuda","ATG"),("Argentina","ARG"),("Armenia","ARM"),
    ("Australia","AUS"),("Austria","AUT"),("Azerbaijan","AZE"),("Bahamas","BHS"),
    ("Bahrain","BHR"),("Bangladesh","BGD"),("Barbados","BRB"),("Belarus","BLR"),
    ("Belgium","BEL"),("Belize","BLZ"),("Benin","BEN"),("Bhutan","BTN"),
    ("Bolivia","BOL"),("Bosnia and Herzegovina","BIH"),("Botswana","BWA"),
    ("Brazil","BRA"),("Brunei","BRN"),("Bulgaria","BGR"),("Burkina Faso","BFA"),
    ("Burundi","BDI"),("Cabo Verde","CPV"),("Cambodia","KHM"),("Cameroon","CMR"),
    ("Canada","CAN"),("Central African Republic","CAF"),("Chad","TCD"),("Chile","CHL"),
    ("China","CHN"),("Colombia","COL"),("Comoros","COM"),("Congo","COG"),
    ("Costa Rica","CRI"),("Côte d'Ivoire","CIV"),("Croatia","HRV"),("Cuba","CUB"),
    ("Cyprus","CYP"),("Czechia","CZE"),("Democratic Republic of the Congo","COD"),
    ("Denmark","DNK"),("Djibouti","DJI"),("Dominica","DMA"),("Dominican Republic","DOM"),
    ("Ecuador","ECU"),("Egypt","EGY"),("El Salvador","SLV"),("Equatorial Guinea","GNQ"),
    ("Eritrea","ERI"),("Estonia","EST"),("Eswatini","SWZ"),("Ethiopia","ETH"),
    ("Fiji","FJI"),("Finland","FIN"),("France","FRA"),("Gabon","GAB"),("Gambia","GMB"),
    ("Georgia","GEO"),("Germany","DEU"),("Ghana","GHA"),("Greece","GRC"),("Grenada","GRD"),
    ("Guatemala","GTM"),("Guinea","GIN"),("Guinea-Bissau","GNB"),("Guyana","GUY"),
    ("Haiti","HTI"),("Honduras","HND"),("Hungary","HUN"),("Iceland","ISL"),("India","IND"),
    ("Indonesia","IDN"),("Iran","IRN"),("Iraq","IRQ"),("Ireland","IRL"),("Israel","ISR"),
    ("Italy","ITA"),("Jamaica","JAM"),("Japan","JPN"),("Jordan","JOR"),("Kazakhstan","KAZ"),
    ("Kenya","KEN"),("Kiribati","KIR"),("Kuwait","KWT"),("Kyrgyzstan","KGZ"),("Laos","LAO"),
    ("Latvia","LVA"),("Lebanon","LBN"),("Lesotho","LSO"),("Liberia","LBR"),("Libya","LBY"),
    ("Liechtenstein","LIE"),("Lithuania","LTU"),("Luxembourg","LUX"),("Madagascar","MDG"),
    ("Malawi","MWI"),("Malaysia","MYS"),("Maldives","MDV"),("Mali","MLI"),("Malta","MLT"),
    ("Marshall Islands","MHL"),("Mauritania","MRT"),("Mauritius","MUS"),("Mexico","MEX"),
    ("Micronesia","FSM"),("Moldova","MDA"),("Monaco","MCO"),("Mongolia","MNG"),
    ("Montenegro","MNE"),("Morocco","MAR"),("Mozambique","MOZ"),("Myanmar","MMR"),
    ("Namibia","NAM"),("Nauru","NRU"),("Nepal","NPL"),("Netherlands","NLD"),
    ("New Zealand","NZL"),("Nicaragua","NIC"),("Niger","NER"),("Nigeria","NGA"),
    ("North Korea","PRK"),("North Macedonia","MKD"),("Norway","NOR"),("Oman","OMN"),
    ("Pakistan","PAK"),("Palau","PLW"),("Palestine","PSE"),("Panama","PAN"),
    ("Papua New Guinea","PNG"),("Paraguay","PRY"),("Peru","PER"),("Philippines","PHL"),
    ("Poland","POL"),("Portugal","PRT"),("Qatar","QAT"),("Romania","ROU"),("Russia","RUS"),
    ("Rwanda","RWA"),("Saint Kitts and Nevis","KNA"),("Saint Lucia","LCA"),
    ("Saint Vincent and the Grenadines","VCT"),("Samoa","WSM"),("San Marino","SMR"),
    ("Sao Tome and Principe","STP"),("Saudi Arabia","SAU"),("Senegal","SEN"),
    ("Serbia","SRB"),("Seychelles","SYC"),("Sierra Leone","SLE"),("Singapore","SGP"),
    ("Slovakia","SVK"),("Slovenia","SVN"),("Solomon Islands","SLB"),("Somalia","SOM"),
    ("South Africa","ZAF"),("South Korea","KOR"),("South Sudan","SSD"),("Spain","ESP"),
    ("Sri Lanka","LKA"),("Sudan","SDN"),("Suriname","SUR"),("Sweden","SWE"),
    ("Switzerland","CHE"),("Syria","SYR"),("Tajikistan","TJK"),("Tanzania","TZA"),
    ("Thailand","THA"),("Timor-Leste","TLS"),("Togo","TGO"),("Tonga","TON"),
    ("Trinidad and Tobago","TTO"),("Tunisia","TUN"),("Türkiye","TUR"),
    ("Turkmenistan","TKM"),("Tuvalu","TUV"),("Uganda","UGA"),("Ukraine","UKR"),
    ("United Arab Emirates","ARE"),("United Kingdom","GBR"),("United States","USA"),
    ("Uruguay","URY"),("Uzbekistan","UZB"),("Vanuatu","VUT"),("Vatican City","VAT"),
    ("Venezuela","VEN"),("Vietnam","VNM"),("Yemen","YEM"),("Zambia","ZMB"),("Zimbabwe","ZWE")
]

WORLD_COUNTRIES = [country for country, iso in COUNTRY_ISO3]


def calculate_risk(exposure, vulnerability, adaptive_capacity, sensitivity, criticality):
    score = (
        0.30 * exposure
        + 0.25 * vulnerability
        + 0.20 * sensitivity
        + 0.15 * criticality
        + 0.10 * (100 - adaptive_capacity)
    )
    score = max(0, min(100, score))

    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Moderate"
    else:
        level = "Low"

    return score, level


def calculate_chri_proxy(
    hazard_pressure,
    population_vulnerability,
    health_readiness
):
    score = (
        0.45 * hazard_pressure
        + 0.35 * population_vulnerability
        + 0.20 * (100 - health_readiness)
    )
    return max(0, min(100, score))


def calculate_ghg(
    electricity_mwh,
    fuel_litres,
    travel_km,
    lifetime_years,
    electricity_ef=0.4,
    fuel_ef=2.68,
    travel_ef=0.18
):
    electricity_t = electricity_mwh * electricity_ef
    fuel_t = fuel_litres * fuel_ef / 1000
    travel_t = travel_km * travel_ef / 1000

    annual = electricity_t + fuel_t + travel_t

    return {
        "electricity_tco2e": electricity_t,
        "fuel_tco2e": fuel_t,
        "travel_tco2e": travel_t,
        "annual_tco2e": annual,
        "lifetime_tco2e": annual * lifetime_years
    }


def build_mitigation_plan(hazard_df):
    actions = {
        "Flood": "Upgrade drainage, floodproof critical assets, and strengthen early warning.",
        "Extreme heat": "Use heat action plans, shade, cooling, and heat-resilient design.",
        "Extreme precipitation": "Increase stormwater capacity and protect drainage crossings.",
        "Wildfire": "Improve fire preparedness, emergency access, and defensible space.",
        "Drought": "Improve water efficiency, storage, reuse, and drought contingency plans.",
        "Landslide": "Use slope stabilization, drainage control, and geotechnical monitoring.",
        "Storm": "Strengthen structures, emergency plans, backup power, and communications.",
        "Sea-level rise": "Use resilient siting, flood protection, and adaptation design."
    }

    rows = []

    for _, row in hazard_df.iterrows():
        score = float(row["Score"])

        if score >= 70:
            priority = "High"
        elif score >= 40:
            priority = "Moderate"
        else:
            priority = "Low"

        rows.append({
            "Hazard": row["Hazard"],
            "Risk score": round(score, 1),
            "Priority": priority,
            "Recommended action": actions.get(
                row["Hazard"],
                "Conduct a detailed climate-risk assessment."
            )
        })

    return rows


def calculate_hazard_scores(exposure, vulnerability, adaptive_capacity, sensitivity, criticality, climate_division, scenario, horizon):
    scenario_factor = {"Low": 0.85, "Moderate": 1.00, "High": 1.18}[scenario]
    horizon_factor = {"Near term": 0.92, "Mid century": 1.05, "Long term": 1.18}[horizon]
    bias = {
        "Flood": {"Tropical":12,"Dry / Arid":3,"Temperate":6,"Continental":5,"Polar":2,"Highland / Mountain":9},
        "Extreme heat": {"Tropical":10,"Dry / Arid":18,"Temperate":5,"Continental":8,"Polar":1,"Highland / Mountain":4},
        "Extreme precipitation": {"Tropical":10,"Dry / Arid":2,"Temperate":6,"Continental":5,"Polar":3,"Highland / Mountain":8},
        "Wildfire": {"Tropical":4,"Dry / Arid":14,"Temperate":10,"Continental":12,"Polar":2,"Highland / Mountain":9},
        "Drought": {"Tropical":5,"Dry / Arid":20,"Temperate":7,"Continental":10,"Polar":1,"Highland / Mountain":6},
        "Landslide": {"Tropical":7,"Dry / Arid":4,"Temperate":6,"Continental":5,"Polar":3,"Highland / Mountain":22},
        "Storm": {"Tropical":18,"Dry / Arid":5,"Temperate":8,"Continental":6,"Polar":5,"Highland / Mountain":4},
        "Sea-level rise": {"Tropical":12,"Dry / Arid":8,"Temperate":7,"Continental":1,"Polar":5,"Highland / Mountain":0},
    }
    base = 0.36*exposure + 0.24*vulnerability + 0.18*sensitivity + 0.10*criticality + 0.12*(100-adaptive_capacity)
    rows=[]
    for i, hazard in enumerate(HAZARDS):
        score = base * scenario_factor * horizon_factor * (0.82 + (i % 4)*0.07) + bias[hazard].get(climate_division, 0)
        score = max(0, min(100, score))
        priority = "High" if score >= 70 else "Moderate" if score >= 40 else "Low"
        rows.append({"Hazard": hazard, "Score": round(score,1), "Priority": priority})
    return pd.DataFrame(rows)


# Broad location profiles used only for interactive screening. These are NOT
# observed climate datasets. They let the simulator react to country selection
# without pretending to provide authoritative country climate projections.
COUNTRY_LOCATION_FACTORS = {
    # country: (temperature sensitivity, precipitation sensitivity, coastal/storm sensitivity,
    #           water/drought sensitivity, mountain/landslide sensitivity)
    "Pakistan": (1.10, 1.05, 0.90, 1.20, 1.10),
    "India": (1.08, 1.05, 1.00, 1.15, 1.05),
    "Bangladesh": (1.05, 1.15, 1.30, 1.00, 0.90),
    "Nepal": (1.05, 1.00, 0.70, 1.00, 1.35),
    "Bhutan": (1.00, 0.95, 0.65, 0.95, 1.40),
    "China": (1.02, 1.00, 1.00, 1.00, 1.10),
    "Japan": (1.00, 1.05, 1.35, 0.90, 1.05),
    "Philippines": (1.05, 1.10, 1.40, 0.95, 0.95),
    "Indonesia": (1.00, 1.10, 1.35, 0.90, 0.90),
    "Australia": (1.08, 0.90, 1.05, 1.25, 0.75),
    "United States": (1.00, 0.95, 1.10, 1.00, 0.85),
    "Canada": (0.95, 0.90, 0.95, 0.80, 0.95),
    "Brazil": (1.00, 1.05, 0.90, 1.00, 0.90),
    "United Kingdom": (0.90, 1.00, 1.10, 0.75, 0.70),
    "Norway": (0.85, 0.95, 1.05, 0.70, 1.05),
    "Switzerland": (0.90, 0.90, 0.55, 0.75, 1.35),
    "South Africa": (1.05, 0.90, 1.00, 1.20, 0.75),
    "Nigeria": (1.10, 1.05, 1.10, 1.15, 0.60),
    "Egypt": (1.15, 0.75, 1.00, 1.35, 0.45),
    "Saudi Arabia": (1.20, 0.65, 0.75, 1.45, 0.45),
    "United Arab Emirates": (1.20, 0.60, 0.90, 1.40, 0.35),
    "Kenya": (1.05, 1.00, 0.90, 1.15, 0.85),
    "Ethiopia": (1.05, 1.00, 0.65, 1.15, 1.05),
    "Mexico": (1.10, 0.90, 1.15, 1.25, 0.80),
    "Peru": (1.05, 1.00, 1.00, 1.10, 1.30),
    "Chile": (1.00, 0.85, 1.15, 1.20, 1.25),
    "Argentina": (1.00, 0.90, 0.95, 1.00, 0.85),
    "New Zealand": (0.95, 1.00, 1.20, 0.75, 1.10),
    "Fiji": (1.05, 1.10, 1.45, 0.95, 0.80),
    "Maldives": (1.05, 1.05, 1.55, 1.00, 0.30),
    "Nauru": (1.05, 1.00, 1.55, 1.00, 0.25),
    "Jamaica": (1.05, 1.10, 1.35, 1.00, 0.70),
    "Iceland": (0.80, 0.90, 1.00, 0.55, 0.85),
}


DIVISION_CLIMATE_FACTORS = {
    "Tropical": (1.05, 1.08, 1.18, 1.00, 0.75),
    "Dry / Arid": (1.18, 0.72, 0.80, 1.35, 0.55),
    "Temperate": (0.95, 1.00, 0.95, 0.85, 0.75),
    "Continental": (1.02, 0.92, 0.85, 0.95, 0.80),
    "Polar": (0.75, 0.88, 0.75, 0.55, 0.85),
    "Highland / Mountain": (0.90, 1.02, 0.70, 0.85, 1.40),
}


def climate_simulation_profile(country, climate_division, scenario, horizon,
                               exposure, vulnerability, adaptive_capacity,
                               sensitivity, criticality):
    """Dynamic climate screening model.

    This is an illustrative screening model, not an observed climate forecast.
    Country, climate division, scenario, horizon and all five project-risk
    inputs affect the returned values.
    """
    # Scenario controls the magnitude of the scenario pathway.
    scenario_factor = {"Low": 0.72, "Moderate": 1.00, "High": 1.32}[scenario]

    # Horizon controls how much of the pathway is realized by the selected horizon.
    horizon_factor = {
        "Near term": 0.48,
        "Mid century": 0.88,
        "Long term": 1.38,
    }[horizon]

    # Country-specific screening modifier. Existing profiles are used where
    # available; other countries receive a transparent, repeatable regional
    # fallback based on their ISO-3 code. This is NOT authoritative climate data.
    iso_lookup = dict(COUNTRY_ISO3)
    iso = iso_lookup.get(country, "ZZZ")
    country_f = COUNTRY_LOCATION_FACTORS.get(country)

    if country_f is None:
        # Repeatable location modifier for countries without a curated profile.
        # It is deliberately kept close to 1.0 so it does not masquerade as
        # measured climate data.
        code_value = sum(ord(ch) for ch in iso)
        country_f = (
            0.94 + (code_value % 13) / 100,
            0.92 + ((code_value * 3) % 17) / 100,
            0.88 + ((code_value * 5) % 22) / 100,
            0.90 + ((code_value * 7) % 20) / 100,
            0.86 + ((code_value * 11) % 25) / 100,
        )

    division_f = DIVISION_CLIMATE_FACTORS.get(
        climate_division, (1, 1, 1, 1, 1)
    )

    # Project risk pressure: all five sidebar inputs affect climate stress.
    # Adaptive capacity is protective, so it enters inversely.
    risk_pressure = (
        0.30 * exposure
        + 0.24 * vulnerability
        + 0.18 * sensitivity
        + 0.16 * criticality
        + 0.12 * (100 - adaptive_capacity)
    ) / 100.0

    # Separate vulnerability and resilience effects make the response visibly
    # change when users move the sliders.
    vulnerability_effect = 0.78 + 0.44 * (
        0.60 * vulnerability / 100
        + 0.40 * sensitivity / 100
    )
    resilience_effect = 1.12 - 0.34 * adaptive_capacity / 100
    criticality_effect = 0.90 + 0.20 * criticality / 100
    exposure_effect = 0.86 + 0.28 * exposure / 100

    project_multiplier = (
        vulnerability_effect
        * resilience_effect
        * criticality_effect
        * exposure_effect
    )

    # Blend country and climate-division characteristics.
    temp_factor = 0.60 * country_f[0] + 0.40 * division_f[0]
    precip_factor = 0.60 * country_f[1] + 0.40 * division_f[1]
    storm_factor = 0.60 * country_f[2] + 0.40 * division_f[2]
    drought_factor = 0.60 * country_f[3] + 0.40 * division_f[3]
    mountain_factor = 0.60 * country_f[4] + 0.40 * division_f[4]

    # Base scenario pathway from Low / Moderate / High.
    base_temp = SCENARIOS[scenario][horizon]["temperature_delta"]
    base_precip = SCENARIOS[scenario][horizon]["precipitation_pct"]

    # Risk-aware response. Higher project risk amplifies planning pressure,
    # while adaptive capacity dampens it through project_multiplier.
    response_scale = (
        (0.82 + 0.38 * risk_pressure)
        * project_multiplier
        * horizon_factor
        * scenario_factor
    )

    temperature_change = base_temp * temp_factor * response_scale
    precipitation_change = base_precip * precip_factor * response_scale

    # Hazard-specific climate response. These values feed the climate charts
    # and can also be used by the mitigation module.
    climate_hazard = {
        "Extreme heat": (
            0.34 * risk_pressure
            + 0.34 * temp_factor / 1.20
            + 0.16 * sensitivity / 100
            + 0.08 * exposure / 100
        ),
        "Flood": (
            0.24 * risk_pressure
            + 0.28 * precip_factor / 1.20
            + 0.16 * storm_factor / 1.35
            + 0.10 * exposure / 100
            + 0.06 * criticality / 100
        ),
        "Extreme precipitation": (
            0.25 * risk_pressure
            + 0.34 * precip_factor / 1.20
            + 0.14 * storm_factor / 1.35
            + 0.08 * exposure / 100
        ),
        "Wildfire": (
            0.26 * risk_pressure
            + 0.32 * drought_factor / 1.35
            + 0.18 * temp_factor / 1.20
            + 0.08 * sensitivity / 100
        ),
        "Drought": (
            0.28 * risk_pressure
            + 0.36 * drought_factor / 1.35
            + 0.12 * (2.0 - precip_factor / 1.20)
            + 0.08 * vulnerability / 100
        ),
        "Landslide": (
            0.22 * risk_pressure
            + 0.36 * mountain_factor / 1.40
            + 0.18 * precip_factor / 1.20
            + 0.08 * criticality / 100
        ),
        "Storm": (
            0.24 * risk_pressure
            + 0.42 * storm_factor / 1.55
            + 0.10 * exposure / 100
            + 0.06 * criticality / 100
        ),
        "Sea-level rise": (
            0.18 * risk_pressure
            + 0.44 * storm_factor / 1.55
            + 0.12 * exposure / 100
            + 0.06 * criticality / 100
        ),
    }

    hazards = {}
    for hazard, raw in climate_hazard.items():
        score = 100 * raw * scenario_factor * horizon_factor * (
            0.86 + 0.28 * project_multiplier
        )
        hazards[hazard] = round(max(0, min(100, score)), 1)

    return {
        "country": country,
        "iso3": iso,
        "climate_division": climate_division,
        "scenario": scenario,
        "horizon": horizon,
        "risk_pressure": round(risk_pressure * 100, 1),
        "project_multiplier": round(project_multiplier, 3),
        "temperature_change": round(temperature_change, 2),
        "precipitation_change": round(precipitation_change, 1),
        "hazards": hazards,
        "temperature_factor": round(temp_factor, 3),
        "precipitation_factor": round(precip_factor, 3),
        "country_modifier": round(sum(country_f) / len(country_f), 3),
        "division_modifier": round(sum(division_f) / len(division_f), 3),
    }


# Sector-specific climate-driver weights. These are transparent screening
# assumptions, not empirical impact models. Each sector responds to a different
# combination of climate hazards.
SECTOR_HAZARD_WEIGHTS = {
    "Agriculture": {
        "Extreme heat": 0.22, "Drought": 0.22, "Extreme precipitation": 0.16,
        "Flood": 0.16, "Storm": 0.08, "Wildfire": 0.08,
        "Landslide": 0.05, "Sea-level rise": 0.03,
    },
    "Water": {
        "Drought": 0.24, "Flood": 0.22, "Extreme precipitation": 0.20,
        "Sea-level rise": 0.12, "Extreme heat": 0.10, "Storm": 0.07,
        "Landslide": 0.03, "Wildfire": 0.02,
    },
    "Health": {
        "Extreme heat": 0.28, "Flood": 0.15, "Drought": 0.13,
        "Wildfire": 0.12, "Storm": 0.11, "Extreme precipitation": 0.10,
        "Sea-level rise": 0.06, "Landslide": 0.05,
    },
    "Transportation": {
        "Flood": 0.20, "Extreme precipitation": 0.20, "Storm": 0.18,
        "Landslide": 0.15, "Extreme heat": 0.10, "Wildfire": 0.08,
        "Sea-level rise": 0.06, "Drought": 0.03,
    },
    "Energy": {
        "Extreme heat": 0.20, "Storm": 0.19, "Flood": 0.18,
        "Drought": 0.15, "Wildfire": 0.10, "Sea-level rise": 0.08,
        "Extreme precipitation": 0.07, "Landslide": 0.03,
    },
}

SECTOR_RISK_WEIGHTS = {
    "Agriculture": {"exposure": 0.24, "vulnerability": 0.25, "adaptive": 0.14, "sensitivity": 0.22, "criticality": 0.15},
    "Water": {"exposure": 0.25, "vulnerability": 0.22, "adaptive": 0.13, "sensitivity": 0.20, "criticality": 0.20},
    "Health": {"exposure": 0.20, "vulnerability": 0.28, "adaptive": 0.15, "sensitivity": 0.25, "criticality": 0.12},
    "Transportation": {"exposure": 0.27, "vulnerability": 0.18, "adaptive": 0.15, "sensitivity": 0.18, "criticality": 0.22},
    "Energy": {"exposure": 0.25, "vulnerability": 0.18, "adaptive": 0.17, "sensitivity": 0.20, "criticality": 0.20},
}

def calculate_sector_profile(
    sector, country, climate_division, scenario, horizon,
    exposure, vulnerability, adaptive_capacity, sensitivity, criticality
):
    """Recalculate a sector profile from all project and climate controls."""
    if sector not in SECTORS:
        raise ValueError(f"Unknown sector: {sector}")

    climate = climate_simulation_profile(
        country, climate_division, scenario, horizon,
        exposure, vulnerability, adaptive_capacity, sensitivity, criticality
    )

    rw = SECTOR_RISK_WEIGHTS[sector]
    project_pressure = (
        exposure * rw["exposure"]
        + vulnerability * rw["vulnerability"]
        + (100 - adaptive_capacity) * rw["adaptive"]
        + sensitivity * rw["sensitivity"]
        + criticality * rw["criticality"]
    )

    # Sector climate pressure is driven by the hazards most relevant to that sector.
    hw = SECTOR_HAZARD_WEIGHTS[sector]
    hazard_contributions = {
        h: climate["hazards"].get(h, 0) * w
        for h, w in hw.items()
    }
    climate_pressure = sum(hazard_contributions.values())

    # Country and climate-division modifiers are already embedded in the
    # climate profile. The blend below makes both project risk and climate
    # pressure materially affect the sector score.
    sector_factor = {
        "Agriculture": 1.04,
        "Water": 1.06,
        "Health": 1.02,
        "Transportation": 0.98,
        "Energy": 1.00,
    }[sector]

    stress = (
        0.52 * project_pressure
        + 0.48 * climate_pressure
    ) * sector_factor
    stress = max(0, min(100, stress))

    # Existing resilience changes dynamically with adaptive capacity and
    # remaining risk gap. Higher adaptive capacity increases resilience.
    resilience = (
        0.72 * adaptive_capacity
        + 0.28 * (100 - stress)
    )
    resilience = max(0, min(100, resilience))

    risk_gap = max(0, min(100, stress - resilience + 50))
    priority = "High" if stress >= 70 else "Moderate" if stress >= 40 else "Low"

    top_drivers = sorted(
        hazard_contributions.items(),
        key=lambda x: x[1],
        reverse=True
    )
    top_driver = top_drivers[0][0]
    top_driver_score = climate["hazards"][top_driver]

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
        "top_driver_score": round(top_driver_score, 1),
        "hazard_contributions": {k: round(v, 2) for k, v in hazard_contributions.items()},
    }


def build_dynamic_plan(hazard_df, selected_hazards, sector, climate_division, scenario, horizon, adaptive_capacity, vulnerability, sensitivity, criticality):
    library = {
        "Flood": ("Adaptation", "Upgrade drainage, floodproof critical assets, and improve early warning.", "Critical assets protected (%)", "Engineering / disaster management"),
        "Extreme heat": ("Adaptation + mitigation", "Use heat action plans, shade, cooling, and heat-resilient design; improve energy efficiency.", "Facilities with heat plan (%)", "Project management / health authority"),
        "Extreme precipitation": ("Adaptation", "Increase stormwater capacity and protect drainage crossings.", "Drainage capacity upgraded (%)", "Engineering / municipal authority"),
        "Wildfire": ("Adaptation", "Improve fire preparedness, emergency access, and defensible space.", "High-risk area with fire plan (%)", "Emergency management / forestry"),
        "Drought": ("Adaptation + mitigation", "Improve water efficiency, storage, reuse, drought monitoring and efficient pumping.", "Demand covered by resilient supply (%)", "Water utility / project owner"),
        "Landslide": ("Adaptation", "Use slope stabilization, drainage control, and geotechnical monitoring.", "High-risk slopes monitored (%)", "Geotechnical / infrastructure team"),
        "Storm": ("Resilience + continuity", "Strengthen structures, emergency plans, backup power and communications.", "Critical services with backup (%)", "Project owner / emergency management"),
        "Sea-level rise": ("Adaptation", "Use resilient siting, elevation, flood protection, and coastal planning.", "Critical coastal assets protected (%)", "Coastal planning / infrastructure"),
    }
    focus = {
        "Agriculture":"protect crops, soil moisture and farm water",
        "Water":"protect water availability, treatment and distribution",
        "Health":"protect health services and vulnerable populations",
        "Transportation":"protect roads, bridges, mobility and emergency access",
        "Energy":"protect generation, distribution and backup power",
    }[sector]
    rows=[]
    for _, row in hazard_df.iterrows():
        if row["Hazard"] not in selected_hazards:
            continue
        score=float(row["Score"])
        action_type, action, kpi, party=library[row["Hazard"]]
        if vulnerability >= 70 or sensitivity >= 70:
            action_type="Adaptation priority"
        elif criticality >= 75:
            action_type="Resilience + continuity"
        timeframe="0–12 months" if score >= 75 else "1–3 years" if score >= 55 else "3–5 years"
        resource_index=0.50*score+0.20*vulnerability+0.20*(100-adaptive_capacity)+0.10*criticality
        resource="Very high" if resource_index >= 75 else "High" if resource_index >= 55 else "Medium" if resource_index >= 35 else "Low"
        target=min(95,max(30,round(40+0.50*score)))
        rows.append({
            "Hazard":row["Hazard"], "Risk score":round(score,1), "Priority":row["Priority"], "Sector":sector,
            "Action type":action_type, "Recommended action":action+f" Prioritize measures that {focus}.",
            "KPI":f"{kpi} — target {target}%", "Timeframe":timeframe,
            "Estimated resource level":resource, "Responsible party":party,
            "Climate division":climate_division, "Scenario":scenario, "Horizon":horizon, "Status":"Not started"
        })
    return pd.DataFrame(rows)
