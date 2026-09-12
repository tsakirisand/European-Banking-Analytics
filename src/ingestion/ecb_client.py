import urllib.request
import ssl
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from src.ingestion.validator import ObservationSchema, normalize_period_to_date

logger = logging.getLogger("ECBClient")

BASE_URL = "https://data-api.ecb.europa.eu/service/data"

class ECBClient:
    def __init__(self):
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def fetch_series(self, dataset_code: str, series_key: str, start_period: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetches data from ECB SDMX REST API for a given dataset and exact series key.
        URL format: https://data-api.ecb.europa.eu/service/data/{dataset}/{key}?format=jsondata&detail=dataonly
        """
        url = f"{BASE_URL}/{dataset_code}/{series_key}?format=jsondata&detail=dataonly"
        if start_period:
            url += f"&startPeriod={start_period}"

        req = urllib.request.Request(url, headers={
            "User-Agent": "EuropeanBankingAnalytics/1.0",
            "Accept": "application/json"
        })

        try:
            with urllib.request.urlopen(req, context=self.ctx, timeout=15) as resp:
                if resp.status != 200:
                    logger.error(f"ECB API error {resp.status} for {dataset_code}/{series_key}")
                    return []
                payload = json.loads(resp.read().decode("utf-8"))
                return self._parse_sdmx_json(dataset_code, series_key, payload)
        except Exception as e:
            logger.error(f"Failed to fetch ECB series {dataset_code}/{series_key}: {e}")
            return []

    def _parse_sdmx_json(self, dataset_code: str, series_key: str, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        observations = []
        try:
            datasets = payload.get("dataSets", [])
            if not datasets:
                return []
            
            series_dict = datasets[0].get("series", {})
            structure = payload.get("structure", {})
            dimensions = structure.get("dimensions", {})
            
            # Extract time dimension values (period labels like '2023-01', '2023-Q1', etc.)
            observation_dims = dimensions.get("observation", [])
            time_periods = []
            for dim in observation_dims:
                if dim.get("id") == "TIME_PERIOD":
                    time_periods = [v.get("id") for v in dim.get("values", [])]
                    break
            
            # Find frequency and geo from series dimensions or series key
            key_parts = series_key.split(".")
            frequency = key_parts[0] if len(key_parts) > 0 else "M"
            
            # Geography is typically the second component in SDMX series keys (e.g. MIR.M.DE, BSI.M.U2, FM.B.U2)
            geo = "U2"
            if len(key_parts) > 1:
                potential_geo = key_parts[1]
                if len(potential_geo) in [2, 4]:
                    geo = potential_geo

            retrieval_ts = datetime.now(timezone.utc).isoformat()

            for s_key, s_val in series_dict.items():
                obs_dict = s_val.get("observations", {})
                for time_idx_str, obs_data in obs_dict.items():
                    time_idx = int(time_idx_str)
                    if time_idx < len(time_periods):
                        period = time_periods[time_idx]
                        obs_val = obs_data[0]
                        if obs_val is not None:
                            p_date = normalize_period_to_date(period, frequency)
                            
                            # Validate using Pydantic model
                            try:
                                obs_obj = ObservationSchema(
                                    dataset_code=dataset_code,
                                    series_key=series_key,
                                    geo=geo,
                                    frequency=frequency,
                                    period=period,
                                    period_date=p_date,
                                    obs_value=float(obs_val),
                                    unit="%" if dataset_code in ["FM", "MIR", "CBD2", "BLS"] else "EUR Million",
                                    retrieval_timestamp=retrieval_ts
                                )
                                observations.append(obs_obj.model_dump())
                            except Exception as val_err:
                                logger.warning(f"Validation skipped observation {period} for {series_key}: {val_err}")
        except Exception as e:
            logger.error(f"Error parsing SDMX JSON payload for {series_key}: {e}")

        return observations
