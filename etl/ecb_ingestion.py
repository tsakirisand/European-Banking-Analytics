import logging
from typing import List, Dict, Any
from src.ingestion.ecb_client import ECBClient
from config.countries import EUROPEAN_COUNTRIES
from config.data_dictionary import INDICATORS

logger = logging.getLogger("ECBIngestion")

class ECBIngestion:
    def __init__(self):
        self.client = ECBClient()

    def fetch_all_ecb_indicators(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetches all ECB indicators for policy rates, interest rates, balance sheet items, BLS, and CBD2 across European countries.
        Returns a mapping of table_name -> list of fact records.
        """
        fact_tables = {
            "fact_interest_rates": [],
            "fact_loans_deposits": [],
            "fact_banking_sector": [],
            "fact_lending_survey": []
        }

        # 1. ECB Policy Rates (FM dataset)
        policy_indicators = ["ECB_DFR", "ECB_MRO", "ECB_MLFR"]
        for p_code in policy_indicators:
            meta = INDICATORS[p_code]
            series_key = meta["series_key"]
            # Series key in API URL removes FM. prefix
            api_key = series_key[3:] if series_key.startswith("FM.") else series_key
            logger.info(f"Fetching Policy Rate {p_code}: {api_key}")
            obs = self.client.fetch_series("FM", api_key)
            for item in obs:
                fact_tables["fact_interest_rates"].append({
                    "country_code": "U2",
                    "indicator_code": p_code,
                    "date_key": item["period"],
                    "obs_value": item["obs_value"],
                    "unit": meta["unit"],
                    "frequency": meta["frequency"]
                })

        # 2. MFI Interest Rates (MIR dataset)
        mir_indicators = ["MIR_MORTGAGE", "MIR_CORPORATE", "MIR_HH_DEPOSIT", "MIR_CORP_DEPOSIT"]
        for geo in EUROPEAN_COUNTRIES.keys():
            for m_code in mir_indicators:
                meta = INDICATORS[m_code]
                series_key = meta["series_template"].format(geo=geo)
                api_key = series_key[4:] if series_key.startswith("MIR.") else series_key
                obs = self.client.fetch_series("MIR", api_key)
                for item in obs:
                    fact_tables["fact_interest_rates"].append({
                        "country_code": geo,
                        "indicator_code": m_code,
                        "date_key": item["period"],
                        "obs_value": item["obs_value"],
                        "unit": meta["unit"],
                        "frequency": meta["frequency"]
                    })

        # 3. Balance Sheet Items (BSI dataset)
        bsi_indicators = ["BSI_HOUSING_LOANS", "BSI_CONSUMER_CREDIT", "BSI_CORP_LOANS"]
        for geo in ["U2", "DE", "FR", "IT", "ES", "NL", "BE", "AT", "GR"]:
            for b_code in bsi_indicators:
                meta = INDICATORS[b_code]
                series_key = meta["series_template"].format(geo=geo)
                api_key = series_key[4:] if series_key.startswith("BSI.") else series_key
                obs = self.client.fetch_series("BSI", api_key)
                for item in obs:
                    fact_tables["fact_loans_deposits"].append({
                        "country_code": geo,
                        "indicator_code": b_code,
                        "date_key": item["period"],
                        "obs_value": item["obs_value"],
                        "unit": meta["unit"],
                        "frequency": meta["frequency"]
                    })

        # 4. Bank Lending Survey (BLS dataset)
        for geo in ["DE", "FR", "IT", "ES", "NL", "GR", "U2"]:
            meta = INDICATORS["BLS_ENTERPRISE_STANDARDS"]
            series_key = meta["series_template"].format(geo=geo)
            api_key = series_key[4:] if series_key.startswith("BLS.") else series_key
            obs = self.client.fetch_series("BLS", api_key)
            for item in obs:
                fact_tables["fact_lending_survey"].append({
                    "country_code": geo,
                    "indicator_code": "BLS_ENTERPRISE_STANDARDS",
                    "date_key": item["period"],
                    "obs_value": item["obs_value"],
                    "unit": meta["unit"],
                    "frequency": meta["frequency"]
                })

        return fact_tables
