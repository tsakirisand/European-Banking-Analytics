import urllib.request
import ssl
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.ingestion.validator import ObservationSchema, normalize_period_to_date

logger = logging.getLogger("EurostatClient")

BASE_URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data"

class EurostatClient:
    def __init__(self):
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def fetch_dataset(self, dataset_code: str, query_params: str, geo: str, frequency: str = "A", unit: str = "") -> List[Dict[str, Any]]:
        """
        Fetches dataset from Eurostat Dissemination API.
        URL format: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{dataset}?lang=EN&{params}
        """
        url = f"{BASE_URL}/{dataset_code}?lang=EN&{query_params}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "EuropeanBankingAnalytics/1.0",
            "Accept": "application/json"
        })

        try:
            with urllib.request.urlopen(req, context=self.ctx, timeout=15) as resp:
                if resp.status != 200:
                    logger.error(f"Eurostat API error {resp.status} for dataset {dataset_code}")
                    return []
                payload = json.loads(resp.read().decode("utf-8"))
                return self._parse_eurostat_json(dataset_code, query_params, geo, frequency, unit, payload)
        except Exception as e:
            logger.error(f"Failed to fetch Eurostat dataset {dataset_code}: {e}")
            return []

    def _parse_eurostat_json(self, dataset_code: str, query_params: str, geo: str, frequency: str, unit: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        observations = []
        try:
            values = payload.get("value", {})
            dimension = payload.get("dimension", {})
            time_dim = dimension.get("time", {}).get("category", {})
            time_indices = time_dim.get("index", {}) # {"2020": 0, "2021": 1, ...}
            
            # Invert time_indices mapping: index -> period label
            idx_to_period = {v: k for k, v in time_indices.items()}
            
            series_key = f"{dataset_code}:{query_params}"
            retrieval_ts = datetime.utcnow().isoformat()

            # If values is a simple dict indexed by string representation of time index
            for idx_str, val in values.items():
                try:
                    idx = int(idx_str)
                    period = idx_to_period.get(idx)
                    if period and val is not None:
                        p_date = normalize_period_to_date(str(period), frequency)
                        obs_obj = ObservationSchema(
                            dataset_code=dataset_code,
                            series_key=series_key,
                            geo=geo,
                            frequency=frequency,
                            period=str(period),
                            period_date=p_date,
                            obs_value=float(val),
                            unit=unit,
                            retrieval_timestamp=retrieval_ts
                        )
                        observations.append(obs_obj.model_dump())
                except Exception as val_err:
                    continue

        except Exception as e:
            logger.error(f"Error parsing Eurostat JSON payload for {dataset_code}: {e}")

        return observations
