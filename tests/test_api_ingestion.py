import pytest
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.ingestion.ecb_client import ECBClient
from src.ingestion.eurostat_client import EurostatClient
from src.ingestion.validator import ObservationSchema, normalize_period_to_date
from src.db.database import Database

def test_normalize_period_to_date():
    assert normalize_period_to_date("2023", "A") == "2023-01-01"
    assert normalize_period_to_date("2023-05", "M") == "2023-05-01"
    assert normalize_period_to_date("2023-Q3", "Q") == "2023-07-01"

def test_observation_schema_validation():
    valid_data = {
        "dataset_code": "MIR",
        "series_key": "MIR.M.DE.B.A2C.A.R.A.2250.EUR.N",
        "geo": "DE",
        "frequency": "M",
        "period": "2023-01",
        "period_date": "2023-01-01",
        "obs_value": 3.75,
        "unit": "%"
    }
    obs = ObservationSchema(**valid_data)
    assert obs.obs_value == 3.75
    assert obs.geo == "DE"
    assert obs.frequency == "M"

def test_observation_schema_invalid_freq():
    invalid_data = {
        "dataset_code": "MIR",
        "series_key": "MIR.M.DE.B.A2C.A.R.A.2250.EUR.N",
        "geo": "DE",
        "frequency": "INVALID",
        "period": "2023-01",
        "obs_value": 3.75
    }
    with pytest.raises(ValueError):
        ObservationSchema(**invalid_data)

def test_live_ecb_client():
    client = ECBClient()
    # Test fetching Deposit Facility Rate
    obs = client.fetch_series("FM", "B.U2.EUR.4F.KR.DFR.LEV")
    assert isinstance(obs, list)
    assert len(obs) > 0
    first_obs = obs[0]
    assert first_obs["dataset_code"] == "FM"
    assert "obs_value" in first_obs

def test_live_eurostat_client():
    client = EurostatClient()
    # Test fetching GDP for Germany
    obs = client.fetch_dataset("nama_10_gdp", "unit=CP_MEUR&na_item=B1GQ&geo=DE", "DE", "A", "EUR Million")
    assert isinstance(obs, list)
    assert len(obs) > 0
    first_obs = obs[0]
    assert first_obs["dataset_code"] == "nama_10_gdp"
    assert first_obs["geo"] == "DE"

def test_database_operations(tmp_path):
    test_db_path = str(tmp_path / "test_banking.db")
    db = Database(test_db_path)
    
    db.register_dataset("FM", "ECB", "Financial Market Rates", "https://data-api.ecb.europa.eu/service/data/FM")
    db.register_series("FM.B.U2.EUR.4F.KR.DFR.LEV", "FM", "Deposit Facility Rate", "U2", "B", "%")
    
    sample_obs = [{
        "dataset_code": "FM",
        "series_key": "FM.B.U2.EUR.4F.KR.DFR.LEV",
        "geo": "U2",
        "frequency": "B",
        "period": "2023-09-20",
        "period_date": "2023-09-20",
        "obs_value": 4.0,
        "unit": "%",
        "retrieval_timestamp": datetime.utcnow().isoformat()
    }]
    
    inserted = db.insert_observations(sample_obs)
    assert inserted == 1
    
    stats = db.fetch_summary_stats()
    assert stats["total_observations"] == 1
    assert stats["total_series"] == 1
    assert stats["total_datasets"] == 1
