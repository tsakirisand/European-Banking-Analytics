import pytest
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.countries import EUROPEAN_COUNTRIES, REGIONS, get_country_info
from config.data_dictionary import DATASETS, INDICATORS
from etl.db_manager import DBManager
from validation.validator import ValidatorEngine
from sql.analytics import AnalyticsEngine

def test_country_config_integrity():
    assert "DE" in EUROPEAN_COUNTRIES
    assert "FR" in EUROPEAN_COUNTRIES
    assert "IT" in EUROPEAN_COUNTRIES
    assert "ES" in EUROPEAN_COUNTRIES
    assert "GR" in EUROPEAN_COUNTRIES
    
    de_info = get_country_info("DE")
    assert de_info["name"] == "Germany"
    assert de_info["region"] == "Western Europe"
    assert de_info["is_ea"] is True
    assert de_info["is_eu"] is True

    gr_info = get_country_info("GR")
    assert gr_info["name"] == "Greece"
    assert gr_info["region"] == "Southern Europe"
    assert gr_info["is_ea"] is True

def test_data_dictionary_completeness():
    assert "FM" in DATASETS
    assert "MIR" in DATASETS
    assert "BSI" in DATASETS
    assert "BLS" in DATASETS
    assert "CBD2" in DATASETS
    assert "nama_10_gdp" in DATASETS

    assert "ECB_DFR" in INDICATORS
    assert "MIR_MORTGAGE" in INDICATORS
    assert "BSI_HOUSING_LOANS" in INDICATORS
    assert "BLS_ENTERPRISE_STANDARDS" in INDICATORS

def test_validator_engine():
    validator = ValidatorEngine()
    
    # Valid record
    rec_pass = {
        "country_code": "DE",
        "indicator_code": "MIR_MORTGAGE",
        "date_key": "2023-01",
        "obs_value": 3.5
    }
    st, msgs = validator.validate_record(rec_pass)
    assert st == "PASS"

    # Negative rate (allowed for DFR / inflation)
    rec_neg = {
        "country_code": "DE",
        "indicator_code": "ECB_DFR",
        "date_key": "2020-01",
        "obs_value": -0.5
    }
    st, _ = validator.validate_record(rec_neg)
    assert st == "PASS"

    # Invalid country
    rec_bad_country = {
        "country_code": "XYZ",
        "indicator_code": "MIR_MORTGAGE",
        "date_key": "2023-01",
        "obs_value": 3.5
    }
    st, _ = validator.validate_record(rec_bad_country)
    assert st == "FAIL"

def test_star_schema_db_manager(tmp_path):
    test_db = str(tmp_path / "test_star.db")
    db = DBManager(test_db)
    
    with db.get_connection() as conn:
        cur = conn.cursor()
        c_cnt = cur.execute("SELECT COUNT(*) FROM dim_country").fetchone()[0]
        s_cnt = cur.execute("SELECT COUNT(*) FROM dim_source").fetchone()[0]
        i_cnt = cur.execute("SELECT COUNT(*) FROM dim_indicator").fetchone()[0]
        
        assert c_cnt >= 26
        assert s_cnt == 10
        assert i_cnt >= 12

    # Insert sample facts
    sample_facts = [{
        "country_code": "DE",
        "indicator_code": "MIR_MORTGAGE",
        "date_key": "2023-01",
        "obs_value": 3.75,
        "unit": "%",
        "frequency": "M"
    }]
    inserted = db.insert_fact_records("fact_interest_rates", sample_facts)
    assert inserted == 1

def test_analytics_engine(tmp_path):
    test_db = str(tmp_path / "test_analytics.db")
    db = DBManager(test_db)
    
    db.insert_fact_records("fact_interest_rates", [
        {"country_code": "DE", "indicator_code": "MIR_MORTGAGE", "date_key": "2023-01", "obs_value": 3.75, "unit": "%", "frequency": "M"},
        {"country_code": "FR", "indicator_code": "MIR_MORTGAGE", "date_key": "2023-01", "obs_value": 3.10, "unit": "%", "frequency": "M"},
        {"country_code": "U2", "indicator_code": "ECB_DFR", "date_key": "2023-01", "obs_value": 2.00, "unit": "%", "frequency": "B"}
    ])

    analytics = AnalyticsEngine(test_db)
    df_rates = analytics.get_interest_rates(["DE", "FR"])
    assert not df_rates.empty
    assert len(df_rates) == 2

    df_snapshot = analytics.get_latest_country_snapshot()
    assert not df_snapshot.empty
    de_row = df_snapshot[df_snapshot["country_code"] == "DE"]
    assert not de_row.empty
    assert de_row.iloc[0]["mortgage_rate"] == 3.75
