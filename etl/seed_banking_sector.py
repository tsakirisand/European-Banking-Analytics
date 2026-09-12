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
            # Add small realistic annual variations
            roe_val = round(base["roe"] * (0.85 + 0.05 * (i % 4) + (0.1 if y >= 2022 else 0)), 2)
            roa_val = round(base["roa"] * (0.85 + 0.05 * (i % 4) + (0.1 if y >= 2022 else 0)), 2)
            npl_val = round(max(0.5, base["npl"] * (1.2 - 0.05 * i)), 2) # Gradual improvement in NPLs
            cet1_val = round(base["cet1"] + 0.2 * i, 2) # Strengthening capital
            lcr_val = round(base["lcr"] + 1.5 * (i % 3), 1)

            records.extend([
                {"country_code": geo, "indicator_code": "CBD2_ROE", "date_key": date_key, "obs_value": roe_val, "unit": "%", "frequency": "A"},
                {"country_code": geo, "indicator_code": "CBD2_ROA", "date_key": date_key, "obs_value": roa_val, "unit": "%", "frequency": "A"},
                {"country_code": geo, "indicator_code": "CBD2_NPL", "date_key": date_key, "obs_value": npl_val, "unit": "%", "frequency": "A"},
                {"country_code": geo, "indicator_code": "CBD2_CET1", "date_key": date_key, "obs_value": cet1_val, "unit": "%", "frequency": "A"},
                {"country_code": geo, "indicator_code": "CBD2_LCR", "date_key": date_key, "obs_value": lcr_val, "unit": "%", "frequency": "A"},
            ])

    return records

def run_seed():
    db = DBManager("european_banking_star.db")
    records = generate_banking_sector_data()
    inserted = db.insert_fact_records("fact_banking_sector", records)
    logger.info(f"Successfully seeded {inserted} records into fact_banking_sector.")

if __name__ == "__main__":
    run_seed()
