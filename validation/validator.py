import logging
from typing import List, Dict, Any, Tuple
from config.countries import EUROPEAN_COUNTRIES
from config.data_dictionary import INDICATORS

logger = logging.getLogger("ValidatorEngine")

class ValidatorEngine:
    def __init__(self):
        self.supported_geos = set(EUROPEAN_COUNTRIES.keys())
        self.supported_indicators = set(INDICATORS.keys())

    def validate_record(self, record: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Validates an observation record.
        Returns (status, list_of_messages) where status is 'PASS', 'FAIL', 'WARNING', or 'UNVERIFIED'.
        """
        messages = []
        status = "PASS"

        # 1. Primary Key / Required fields check
        required_fields = ["country_code", "indicator_code", "date_key", "obs_value"]
        for f in required_fields:
            if f not in record or record[f] is None:
                messages.append(f"Missing required field: {f}")
                status = "FAIL"

        if status == "FAIL":
            return "FAIL", messages

        # 2. Foreign Key checks
        country_code = record["country_code"]
        if country_code not in self.supported_geos:
            messages.append(f"Invalid country code: {country_code}")
            status = "FAIL"

        indicator_code = record["indicator_code"]
        if indicator_code not in self.supported_indicators:
            messages.append(f"Unknown indicator code: {indicator_code}")
            status = "WARNING"

        # 3. Numeric & Bounds check
        try:
            val = float(record["obs_value"])
            # Interest rates or inflation can be negative (e.g. negative deposit facility rate in 2014-2022, negative inflation)
            if val < -50.0 or val > 50000000.0:
                messages.append(f"Extreme observation value detected: {val}")
                status = "WARNING"
        except (ValueError, TypeError):
            messages.append(f"Invalid non-numeric value: {record['obs_value']}")
            status = "FAIL"

        # 4. Period format check
        date_key = str(record["date_key"]).strip()
        if not date_key:
            messages.append("Empty date_key")
            status = "FAIL"

        if not messages:
            messages.append("Record validated successfully.")

        return status, messages

    def validate_batch(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        results = {
            "PASS": 0,
            "FAIL": 0,
            "WARNING": 0,
            "UNVERIFIED": 0,
            "details": []
        }
        for rec in records:
            st, msgs = self.validate_record(rec)
            results[st] += 1
            if st != "PASS":
                results["details"].append({
                    "record_id": f"{rec.get('country_code')}:{rec.get('indicator_code')}:{rec.get('date_key')}",
                    "status": st,
                    "messages": msgs
                })
        return results
