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
    }

    records = []
    # Monthly dates from 2005 to 2025
    total_months = (2025 - 2005 + 1) * 12
    for geo, base in country_loans.items():
        m_idx = 0
        for year in range(2005, 2026):
            for month in range(1, 13):
                date_key = f"{year}-{month:02d}"
                growth = 1.0 + (m_idx / total_months) * 0.45 # Realistic credit growth trajectory
                
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

def run_seed():
    db = DBManager("european_banking_star.db")
    records_bank = generate_banking_sector_data()
    inserted_bank = db.insert_fact_records("fact_banking_sector", records_bank)
    logger.info(f"Successfully seeded {inserted_bank} records into fact_banking_sector.")

    records_loans = generate_loans_deposits_data()
    inserted_loans = db.insert_fact_records("fact_loans_deposits", records_loans)
    logger.info(f"Successfully seeded {inserted_loans} records into fact_loans_deposits.")

if __name__ == "__main__":
    run_seed()
