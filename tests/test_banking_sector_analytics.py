import pytest
import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from etl.db_manager import DBManager
from sql.analytics import AnalyticsEngine

def test_banking_sector_analytics(tmp_path):
    test_db = str(tmp_path / "test_banking_sector.db")
    db = DBManager(test_db)
    
    # Insert sample fact records for banking sector
    db.insert_fact_records("fact_banking_sector", [
        {"country_code": "DE", "indicator_code": "CBD2_ROE", "date_key": "2023", "obs_value": 5.4, "unit": "%", "frequency": "A"},
        {"country_code": "FR", "indicator_code": "CBD2_ROE", "date_key": "2023", "obs_value": 7.8, "unit": "%", "frequency": "A"},
        {"country_code": "DE", "indicator_code": "CBD2_NPL", "date_key": "2023", "obs_value": 1.2, "unit": "%", "frequency": "A"},
        {"country_code": "FR", "indicator_code": "CBD2_CET1", "date_key": "2023", "obs_value": 15.2, "unit": "%", "frequency": "A"},
    ])

    analytics = AnalyticsEngine(test_db)
    df_prof = analytics.get_banking_profitability(["DE", "FR"])
    assert not df_prof.empty
    assert len(df_prof) == 2

    df_risk = analytics.get_banking_risk(["DE", "FR"])
    assert not df_risk.empty
    assert len(df_risk) == 2

    profile = analytics.get_country_full_profile("DE")
    assert "banking" in profile
    assert not profile["banking"].empty
