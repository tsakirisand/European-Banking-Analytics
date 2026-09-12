import logging
from typing import List, Dict, Any
from src.ingestion.eurostat_client import EurostatClient
from config.data_dictionary import INDICATORS

logger = logging.getLogger("EurostatIngestion")

# Target European countries for macro context
MACRO_GEOS = ["DE", "FR", "IT", "ES", "NL", "BE", "AT", "PT", "IE", "FI", "GR", "PL", "CZ", "HU", "SE", "DK", "RO", "BG"]

class EurostatIngestion:
    def __init__(self):
        self.client = EurostatClient()

    def fetch_all_macro_indicators(self) -> List[Dict[str, Any]]:
        """
        Fetches macro indicators from Eurostat (GDP, GDP per capita, Population, Inflation, Household Income).
        Returns a list of fact_macro records.
        """
        records = []
        macro_indicators = ["EUROSTAT_GDP", "EUROSTAT_GDP_PC", "EUROSTAT_POP", "EUROSTAT_HICP", "EUROSTAT_DISP_INC"]

        for geo in MACRO_GEOS:
            for m_code in macro_indicators:
                meta = INDICATORS[m_code]
                query_params = f"{meta['query_params']}&geo={geo}"
                dataset_code = meta["dataset_code"]
                freq = meta["frequency"]
                unit = meta["unit"]

                try:
                    obs = self.client.fetch_dataset(dataset_code, query_params, geo, freq, unit)
                    for item in obs:
                        records.append({
                            "country_code": geo,
                            "indicator_code": m_code,
                            "date_key": item["period"],
                            "obs_value": item["obs_value"],
                            "unit": unit,
                            "frequency": freq
                        })
                except Exception as e:
                    logger.warning(f"Error fetching Eurostat macro indicator {m_code} for {geo}: {e}")

        return records
