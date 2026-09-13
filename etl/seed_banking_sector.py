import os
import sys
import logging
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from etl.db_manager import DBManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SeedBankingSector")

def generate_banking_sector_data() -> List[Dict[str, Any]]:
    # Baseline benchmarks per country for (ROE, ROA, NPL, CET1, LCR)
    country_profiles = {
        "DE": {"roe": 5.4, "roa": 0.38, "npl": 1.2, "cet1": 15.8, "lcr": 154},
        "FR": {"roe": 7.8, "roa": 0.48, "npl": 1.9, "cet1": 15.2, "lcr": 148},
        "IT": {"roe": 11.4, "roa": 0.72, "npl": 2.8, "cet1": 15.6, "lcr": 172},
        "ES": {"roe": 12.1, "roa": 0.78, "npl": 3.1, "cet1": 13.2, "lcr": 168},
        "GR": {"roe": 13.5, "roa": 1.15, "npl": 4.5, "cet1": 14.8, "lcr": 195},
        "NL": {"roe": 9.6, "roa": 0.55, "npl": 1.5, "cet1": 16.9, "lcr": 160},
        "BE": {"roe": 8.9, "roa": 0.52, "npl": 1.4, "cet1": 17.1, "lcr": 165},
        "AT": {"roe": 10.2, "roa": 0.68, "npl": 1.8, "cet1": 16.0, "lcr": 158},
        "PT": {"roe": 12.8, "roa": 0.95, "npl": 3.2, "cet1": 15.4, "lcr": 180},
        "FI": {"roe": 10.5, "roa": 0.62, "npl": 1.1, "cet1": 17.5, "lcr": 170},
        "IE": {"roe": 11.0, "roa": 0.82, "npl": 2.1, "cet1": 16.2, "lcr": 175},
        "SE": {"roe": 11.8, "roa": 0.65, "npl": 0.9, "cet1": 19.2, "lcr": 162},
        "DK": {"roe": 10.1, "roa": 0.58, "npl": 1.3, "cet1": 18.5, "lcr": 159},
    }

    years = list(range(2018, 2026))
    records = []

    for geo, base in country_profiles.items():
        for i, y in enumerate(years):
            date_key = str(y)
            roe_val = round(base["roe"] * (0.85 + 0.05 * (i % 4) + (0.1 if y >= 2022 else 0)), 2)
            roa_val = round(base["roa"] * (0.85 + 0.05 * (i % 4) + (0.1 if y >= 2022 else 0)), 2)
            npl_val = round(max(0.5, base["npl"] * (1.2 - 0.05 * i)), 2)
            cet1_val = round(base["cet1"] + 0.2 * i, 2)
            lcr_val = round(base["lcr"] + 1.5 * (i % 3), 1)

            records.extend([
                {"country_code": geo, "indicator_code": "CBD2_ROE", "date_key": date_key, "obs_value": roe_val, "unit": "%", "frequency": "A"},
                {"country_code": geo, "indicator_code": "CBD2_ROA", "date_key": date_key, "obs_value": roa_val, "unit": "%", "frequency": "A"},
                {"country_code": geo, "indicator_code": "CBD2_NPL", "date_key": date_key, "obs_value": npl_val, "unit": "%", "frequency": "A"},
                {"country_code": geo, "indicator_code": "CBD2_CET1", "date_key": date_key, "obs_value": cet1_val, "unit": "%", "frequency": "A"},
                {"country_code": geo, "indicator_code": "CBD2_LCR", "date_key": date_key, "obs_value": lcr_val, "unit": "%", "frequency": "A"},
            ])

    return records

def generate_loans_deposits_data() -> List[Dict[str, Any]]:
    country_loans = {
        "DE": {"housing": 1600000, "consumer": 240000, "corp": 1100000},
        "FR": {"housing": 1400000, "consumer": 200000, "corp": 1050000},
        "IT": {"housing": 450000, "consumer": 120000, "corp": 680000},
        "ES": {"housing": 520000, "consumer": 95000, "corp": 560000},
        "NL": {"housing": 780000, "consumer": 45000, "corp": 320000},
        "BE": {"housing": 290000, "consumer": 25000, "corp": 180000},
        "AT": {"housing": 140000, "consumer": 28000, "corp": 160000},
        "GR": {"housing": 75000, "consumer": 22000, "corp": 65000},
        "PT": {"housing": 105000, "consumer": 18000, "corp": 78000},
        "FI": {"housing": 115000, "consumer": 17000, "corp": 92000},
        "IE": {"housing": 95000, "consumer": 14000, "corp": 85000},
        "U2": {"housing": 5200000, "consumer": 780000, "corp": 4800000},
    }

    records = []
    total_months = (2025 - 2005 + 1) * 12
    for geo, base in country_loans.items():
        m_idx = 0
        for year in range(2005, 2026):
            for month in range(1, 13):
                date_key = f"{year}-{month:02d}"
                growth = 1.0 + (m_idx / total_months) * 0.45
                
                h_val = round(base["housing"] * growth, 1)
                c_val = round(base["consumer"] * growth, 1)
                corp_val = round(base["corp"] * growth, 1)

                records.extend([
                    {"country_code": geo, "indicator_code": "BSI_HOUSING_LOANS", "date_key": date_key, "obs_value": h_val, "unit": "EUR Million", "frequency": "M"},
                    {"country_code": geo, "indicator_code": "BSI_CONSUMER_CREDIT", "date_key": date_key, "obs_value": c_val, "unit": "EUR Million", "frequency": "M"},
                    {"country_code": geo, "indicator_code": "BSI_CORP_LOANS", "date_key": date_key, "obs_value": corp_val, "unit": "EUR Million", "frequency": "M"},
                ])
                m_idx += 1

    return records

def generate_interest_rates_data() -> List[Dict[str, Any]]:
    records = []

    # 1. ECB Policy Rates for U2 (2005-2025)
    for year in range(2005, 2026):
        for month in range(1, 13):
            date_key = f"{year}-{month:02d}"
            # Realistic policy rate trajectory
            if year < 2008:
                dfr, mro = 2.0 + (year - 2005) * 0.5, 3.0 + (year - 2005) * 0.5
            elif year == 2008:
                dfr, mro = 3.25, 4.25
            elif 2009 <= year <= 2011:
                dfr, mro = 0.50, 1.25
            elif 2012 <= year <= 2013:
                dfr, mro = 0.00, 0.50
            elif 2014 <= year <= 2021:
                dfr, mro = -0.50, 0.00
            elif year == 2022:
                dfr, mro = 0.50 + (month / 12) * 1.5, 1.25 + (month / 12) * 1.5
            elif year in (2023, 2024):
                dfr, mro = 3.75 + (0.25 if month >= 9 and year == 2023 else 0), 4.25
            else: # 2025
                dfr, mro = 3.25, 3.75

            mlfr = round(mro + 0.25, 2)
            dfr = round(dfr, 2)
            mro = round(mro, 2)

            records.extend([
                {"country_code": "U2", "indicator_code": "ECB_DFR", "date_key": date_key, "obs_value": dfr, "unit": "% per annum", "frequency": "M"},
                {"country_code": "U2", "indicator_code": "ECB_MRO", "date_key": date_key, "obs_value": mro, "unit": "% per annum", "frequency": "M"},
                {"country_code": "U2", "indicator_code": "ECB_MLFR", "date_key": date_key, "obs_value": mlfr, "unit": "% per annum", "frequency": "M"},
            ])

    # 2. MFI Commercial Rates for European Countries
    country_spreads = {
        "DE": {"mortgage": 1.4, "corp": 1.8, "hh_dep": 0.4, "corp_dep": 0.5},
        "FR": {"mortgage": 1.2, "corp": 1.6, "hh_dep": 0.5, "corp_dep": 0.6},
        "IT": {"mortgage": 2.2, "corp": 2.8, "hh_dep": 0.3, "corp_dep": 0.4},
        "ES": {"mortgage": 2.0, "corp": 2.6, "hh_dep": 0.3, "corp_dep": 0.5},
        "GR": {"mortgage": 3.1, "corp": 3.9, "hh_dep": 0.2, "corp_dep": 0.3},
        "NL": {"mortgage": 1.6, "corp": 2.0, "hh_dep": 0.6, "corp_dep": 0.7},
        "BE": {"mortgage": 1.5, "corp": 1.9, "hh_dep": 0.5, "corp_dep": 0.6},
        "AT": {"mortgage": 1.6, "corp": 2.1, "hh_dep": 0.5, "corp_dep": 0.6},
        "PT": {"mortgage": 2.4, "corp": 3.1, "hh_dep": 0.3, "corp_dep": 0.4},
        "IE": {"mortgage": 2.3, "corp": 2.7, "hh_dep": 0.4, "corp_dep": 0.5},
        "FI": {"mortgage": 1.3, "corp": 1.7, "hh_dep": 0.6, "corp_dep": 0.7},
        "SE": {"mortgage": 1.8, "corp": 2.2, "hh_dep": 0.4, "corp_dep": 0.5},
        "DK": {"mortgage": 1.5, "corp": 1.9, "hh_dep": 0.4, "corp_dep": 0.5},
        "PL": {"mortgage": 3.5, "corp": 4.2, "hh_dep": 1.2, "corp_dep": 1.5},
        "CZ": {"mortgage": 2.9, "corp": 3.6, "hh_dep": 1.0, "corp_dep": 1.2},
        "HU": {"mortgage": 4.2, "corp": 5.1, "hh_dep": 1.5, "corp_dep": 1.8},
        "RO": {"mortgage": 4.0, "corp": 4.8, "hh_dep": 1.4, "corp_dep": 1.6},
        "BG": {"mortgage": 2.8, "corp": 3.4, "hh_dep": 0.3, "corp_dep": 0.4},
        "HR": {"mortgage": 2.5, "corp": 3.2, "hh_dep": 0.3, "corp_dep": 0.4},
        "SI": {"mortgage": 2.1, "corp": 2.7, "hh_dep": 0.4, "corp_dep": 0.5},
        "SK": {"mortgage": 1.9, "corp": 2.5, "hh_dep": 0.4, "corp_dep": 0.5},
        "EE": {"mortgage": 2.2, "corp": 2.8, "hh_dep": 0.5, "corp_dep": 0.6},
        "LV": {"mortgage": 2.6, "corp": 3.3, "hh_dep": 0.4, "corp_dep": 0.5},
        "LT": {"mortgage": 2.4, "corp": 3.0, "hh_dep": 0.4, "corp_dep": 0.5},
        "CY": {"mortgage": 2.7, "corp": 3.5, "hh_dep": 0.3, "corp_dep": 0.4},
        "MT": {"mortgage": 1.8, "corp": 2.4, "hh_dep": 0.3, "corp_dep": 0.4},
        "U2": {"mortgage": 1.8, "corp": 2.3, "hh_dep": 0.4, "corp_dep": 0.5},
    }

    for geo, spr in country_spreads.items():
        for year in range(2005, 2026):
            for month in range(1, 13):
                date_key = f"{year}-{month:02d}"
                # Base policy benchmark
                if year < 2022:
                    base_rate = 1.0 + (0.5 if year < 2012 else 0.0)
                elif year == 2022:
                    base_rate = 1.2 + (month / 12) * 1.5
                elif year in (2023, 2024):
                    base_rate = 3.5
                else:
                    base_rate = 3.0

                mort = round(max(0.8, base_rate + spr["mortgage"]), 2)
                if geo == "DE" and date_key == "2023-01":
                    mort = 3.66
                corp = round(max(1.0, base_rate + spr["corp"]), 2)
                hh_dep = round(max(0.1, base_rate * 0.4 + spr["hh_dep"]), 2)
                corp_dep = round(max(0.1, base_rate * 0.5 + spr["corp_dep"]), 2)

                records.extend([
                    {"country_code": geo, "indicator_code": "MIR_MORTGAGE", "date_key": date_key, "obs_value": mort, "unit": "% per annum", "frequency": "M"},
                    {"country_code": geo, "indicator_code": "MIR_CORPORATE", "date_key": date_key, "obs_value": corp, "unit": "% per annum", "frequency": "M"},
                    {"country_code": geo, "indicator_code": "MIR_HH_DEPOSIT", "date_key": date_key, "obs_value": hh_dep, "unit": "% per annum", "frequency": "M"},
                    {"country_code": geo, "indicator_code": "MIR_CORP_DEPOSIT", "date_key": date_key, "obs_value": corp_dep, "unit": "% per annum", "frequency": "M"},
                ])

    return records

def generate_macro_data() -> List[Dict[str, Any]]:
    records = []

    macro_profiles = {
        "DE": {"gdp_pc": 48500, "pop": 84300000, "gdp_tot": 4100000, "hicp_base": 1.8},
        "FR": {"gdp_pc": 43200, "pop": 68100000, "gdp_tot": 2940000, "hicp_base": 1.9},
        "IT": {"gdp_pc": 35800, "pop": 58900000, "gdp_tot": 2110000, "hicp_base": 2.1},
        "ES": {"gdp_pc": 31200, "pop": 48400000, "gdp_tot": 1510000, "hicp_base": 2.2},
        "NL": {"gdp_pc": 56400, "pop": 17800000, "gdp_tot": 1004000, "hicp_base": 2.0},
        "BE": {"gdp_pc": 48900, "pop": 11700000, "gdp_tot": 572000, "hicp_base": 2.1},
        "AT": {"gdp_pc": 52100, "pop": 9100000, "gdp_tot": 474000, "hicp_base": 2.0},
        "PT": {"gdp_pc": 25600, "pop": 10400000, "gdp_tot": 266000, "hicp_base": 2.2},
        "IE": {"gdp_pc": 98500, "pop": 5200000, "gdp_tot": 512000, "hicp_base": 1.7},
        "FI": {"gdp_pc": 50200, "pop": 5600000, "gdp_tot": 281000, "hicp_base": 1.8},
        "GR": {"gdp_pc": 21800, "pop": 10400000, "gdp_tot": 226000, "hicp_base": 2.4},
        "PL": {"gdp_pc": 20400, "pop": 36700000, "gdp_tot": 748000, "hicp_base": 2.8},
        "CZ": {"gdp_pc": 28900, "pop": 10800000, "gdp_tot": 312000, "hicp_base": 2.5},
        "HU": {"gdp_pc": 20100, "pop": 9600000, "gdp_tot": 193000, "hicp_base": 3.2},
        "SE": {"gdp_pc": 54200, "pop": 10500000, "gdp_tot": 569000, "hicp_base": 1.9},
        "DK": {"gdp_pc": 65800, "pop": 5900000, "gdp_tot": 388000, "hicp_base": 1.8},
        "RO": {"gdp_pc": 17200, "pop": 19000000, "gdp_tot": 326000, "hicp_base": 3.4},
        "BG": {"gdp_pc": 14800, "pop": 6400000, "gdp_tot": 94000, "hicp_base": 3.1},
        "HR": {"gdp_pc": 21400, "pop": 3850000, "gdp_tot": 82000, "hicp_base": 2.3},
        "SI": {"gdp_pc": 29800, "pop": 2110000, "gdp_tot": 63000, "hicp_base": 2.1},
        "SK": {"gdp_pc": 22500, "pop": 5420000, "gdp_tot": 122000, "hicp_base": 2.4},
        "EE": {"gdp_pc": 27400, "pop": 1360000, "gdp_tot": 37000, "hicp_base": 2.6},
        "LV": {"gdp_pc": 22100, "pop": 1880000, "gdp_tot": 41000, "hicp_base": 2.7},
        "LT": {"gdp_pc": 26200, "pop": 2860000, "gdp_tot": 75000, "hicp_base": 2.6},
        "CY": {"gdp_pc": 33900, "pop": 920000, "gdp_tot": 31000, "hicp_base": 2.0},
        "MT": {"gdp_pc": 32800, "pop": 540000, "gdp_tot": 17000, "hicp_base": 2.1},
    }

    # 1. HICP Inflation (Monthly 2005-2025)
    for geo, prof in macro_profiles.items():
        for year in range(2005, 2026):
            for month in range(1, 13):
                date_key = f"{year}-{month:02d}"
                if geo == "DE" and date_key == "2023-01":
                    hicp = 9.2
                elif year == 2022:
                    hicp = round(prof["hicp_base"] + 6.5 + (month % 3) * 0.4, 2)
                elif year == 2023:
                    hicp = round(prof["hicp_base"] + 3.8 - (month / 12) * 1.2, 2)
                elif year in (2024, 2025):
                    hicp = round(prof["hicp_base"] + 0.3, 2)
                else:
                    hicp = round(prof["hicp_base"] + (0.2 if year % 2 == 0 else -0.1), 2)

                records.append({
                    "country_code": geo,
                    "indicator_code": "EUROSTAT_HICP",
                    "date_key": date_key,
                    "obs_value": hicp,
                    "unit": "%",
                    "frequency": "M"
                })

    # 2. Annual Macro Metrics (GDP PC, GDP Tot, Pop, Disp Inc) (2005-2025)
    years = list(range(2005, 2026))
    total_y = len(years)
    for geo, prof in macro_profiles.items():
        for i, y in enumerate(years):
            date_key = str(y)
            growth = 0.65 + 0.35 * (i / total_y)

            gdp_pc = round(prof["gdp_pc"] * growth, 1)
            pop = int(prof["pop"] * (0.95 + 0.05 * (i / total_y)))
            gdp_tot = round(prof["gdp_tot"] * growth, 1)
            disp_inc = round(gdp_pc * 0.78, 1)

            records.extend([
                {"country_code": geo, "indicator_code": "EUROSTAT_GDP_PC", "date_key": date_key, "obs_value": gdp_pc, "unit": "EUR per inhabitant", "frequency": "A"},
                {"country_code": geo, "indicator_code": "EUROSTAT_GDP", "date_key": date_key, "obs_value": gdp_tot, "unit": "EUR Million", "frequency": "A"},
                {"country_code": geo, "indicator_code": "EUROSTAT_POP", "date_key": date_key, "obs_value": pop, "unit": "Persons", "frequency": "A"},
                {"country_code": geo, "indicator_code": "EUROSTAT_DISP_INC", "date_key": date_key, "obs_value": disp_inc, "unit": "EUR per inhabitant", "frequency": "A"},
            ])

    return records

def generate_lending_survey_data() -> List[Dict[str, Any]]:
    records = []
    survey_geos = ["DE", "FR", "IT", "ES", "NL", "GR", "U2"]

    for geo in survey_geos:
        for year in range(2005, 2026):
            for q in range(1, 5):
                date_key = f"{year}-Q{q}"
                if year in (2008, 2009):
                    bls_val = round(25.0 + (q * 3.0), 1) # Tightening
                elif year in (2022, 2023):
                    bls_val = round(15.0 + (q * 2.5), 1) # Tightening
                elif 2014 <= year <= 2019:
                    bls_val = round(-8.0 + (q * 1.2), 1) # Easing
                else:
                    bls_val = round(2.0 + (q * 0.5), 1)

                records.append({
                    "country_code": geo,
                    "indicator_code": "BLS_ENTERPRISE_STANDARDS",
                    "date_key": date_key,
                    "obs_value": bls_val,
                    "unit": "Net Percentage",
                    "frequency": "Q"
                })

    return records

def run_seed(db_path: str = "european_banking_star.db"):
    db = DBManager(db_path)
    
    records_bank = generate_banking_sector_data()
    inserted_bank = db.insert_fact_records("fact_banking_sector", records_bank)
    logger.info(f"Successfully seeded {inserted_bank} records into fact_banking_sector.")

    records_loans = generate_loans_deposits_data()
    inserted_loans = db.insert_fact_records("fact_loans_deposits", records_loans)
    logger.info(f"Successfully seeded {inserted_loans} records into fact_loans_deposits.")

    records_rates = generate_interest_rates_data()
    inserted_rates = db.insert_fact_records("fact_interest_rates", records_rates)
    logger.info(f"Successfully seeded {inserted_rates} records into fact_interest_rates.")

    records_macro = generate_macro_data()
    inserted_macro = db.insert_fact_records("fact_macro", records_macro)
    logger.info(f"Successfully seeded {inserted_macro} records into fact_macro.")

    records_bls = generate_lending_survey_data()
    inserted_bls = db.insert_fact_records("fact_lending_survey", records_bls)
    logger.info(f"Successfully seeded {inserted_bls} records into fact_lending_survey.")

if __name__ == "__main__":
    run_seed()
