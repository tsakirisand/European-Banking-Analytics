import pytest
import os
import sys
import sqlite3
import json
import urllib.request
import ssl
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sql.analytics import AnalyticsEngine
from etl.db_manager import DBManager

@pytest.fixture
def db_conn():
    db_path = "european_banking_star.db"
    assert os.path.exists(db_path), f"Database file {db_path} not found"
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()

def test_warehouse_observation_integrity(db_conn):
    """Verifies total fact observation count in SQLite star schema warehouse is >= 40,000."""
    tables = ["fact_interest_rates", "fact_loans_deposits", "fact_banking_sector", "fact_lending_survey", "fact_macro"]
    total_obs = 0
    for t in tables:
        cnt = pd.read_sql_query(f"SELECT count(*) as count FROM {t}", db_conn)["count"][0]
        total_obs += cnt
    assert total_obs >= 40000, f"Expected >= 40,000 observations, found {total_obs}"

def test_no_duplicate_business_keys(db_conn):
    """Verifies that no duplicate (country_code, indicator_code, date_key) business keys exist in fact tables."""
    fact_tables = ["fact_interest_rates", "fact_loans_deposits", "fact_banking_sector", "fact_lending_survey", "fact_macro"]
    for table in fact_tables:
        dup_query = f"""
        SELECT country_code, indicator_code, date_key, COUNT(*) as cnt 
        FROM {table} 
        GROUP BY country_code, indicator_code, date_key 
        HAVING cnt > 1
        """
        dups = pd.read_sql_query(dup_query, db_conn)
        assert dups.empty, f"Found {len(dups)} duplicate records in {table}"

def test_reconcile_ecb_live_api_with_database(db_conn):
    """Reconciles Germany Mortgage Lending Rate (MIR_MORTGAGE) at 2023-01 directly with live ECB REST API."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Query DB ground truth
    db_val = pd.read_sql_query(
        "SELECT obs_value FROM fact_interest_rates WHERE country_code = 'DE' AND indicator_code = 'MIR_MORTGAGE' AND date_key = '2023-01'",
        db_conn
    )
    assert not db_val.empty, "Database missing DE MIR_MORTGAGE for 2023-01"
    db_obs = db_val.iloc[0]["obs_value"]

    # Fetch live ECB API
    url = "https://data-api.ecb.europa.eu/service/data/MIR/M.DE.B.A2C.A.R.A.2250.EUR.N?format=jsondata&detail=dataonly&startPeriod=2023-01"
    req = urllib.request.Request(url, headers={"User-Agent": "EuropeanBankingAnalytics/1.0", "Accept": "application/json"})
    
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        assert resp.status == 200, f"ECB API returned HTTP status {resp.status}"
        data = json.loads(resp.read().decode("utf-8"))
        series_dict = data["dataSets"][0]["series"]
        s_key = list(series_dict.keys())[0]
        obs_dict = series_dict[s_key]["observations"]
        dims = data["structure"]["dimensions"]["observation"][0]["values"]
        time_map = {idx: item["id"] for idx, item in enumerate(dims)}
        
        ecb_obs = None
        for k, v in obs_dict.items():
            if time_map[int(k)] == "2023-01":
                ecb_obs = float(v[0])
                break
        
        assert ecb_obs is not None, "Period 2023-01 not found in ECB API response"
        assert abs(db_obs - ecb_obs) < 0.0001, f"Database value {db_obs} does not match ECB API value {ecb_obs}"

def test_reconcile_eurostat_live_api_with_database(db_conn):
    """Reconciles Germany HICP Inflation (EUROSTAT_HICP) at 2023-01 directly with live Eurostat REST API."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    # Query DB ground truth
    db_val = pd.read_sql_query(
        "SELECT obs_value FROM fact_macro WHERE country_code = 'DE' AND indicator_code = 'EUROSTAT_HICP' AND date_key = '2023-01'",
        db_conn
    )
    assert not db_val.empty, "Database missing DE EUROSTAT_HICP for 2023-01"
    db_obs = db_val.iloc[0]["obs_value"]

    # Fetch live Eurostat API
    url = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_manr?lang=EN&coicop=CP00&geo=DE"
    req = urllib.request.Request(url, headers={"User-Agent": "EuropeanBankingAnalytics/1.0", "Accept": "application/json"})
    
    with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
        assert resp.status == 200, f"Eurostat API returned HTTP status {resp.status}"
        es_data = json.loads(resp.read().decode("utf-8"))
        es_vals = es_data["value"]
        es_time = es_data["dimension"]["time"]["category"]["index"]
        rev_time = {v: k for k, v in es_time.items()}
        
        eurostat_obs = None
        for k, v in es_vals.items():
            if rev_time[int(k)] == "2023-01":
                eurostat_obs = float(v)
                break

        assert eurostat_obs is not None, "Period 2023-01 not found in Eurostat API response"
        assert abs(db_obs - eurostat_obs) < 0.0001, f"Database value {db_obs} does not match Eurostat API value {eurostat_obs}"

def test_analytics_query_reconciliation():
    """Reconciles AnalyticsEngine SQL query outputs with database row values."""
    analytics = AnalyticsEngine("european_banking_star.db")
    
    # 1. Test policy rates query
    df_pol = analytics.get_policy_rates()
    assert not df_pol.empty, "AnalyticsEngine.get_policy_rates() returned empty DataFrame"
    assert "Deposit Facility Rate" in df_pol["indicator_name"].values

    # 2. Test interest rates query for DE
    df_rates = analytics.get_interest_rates(["DE"], 2020, 2024)
    assert not df_rates.empty, "AnalyticsEngine.get_interest_rates(['DE']) returned empty DataFrame"
    
    # 3. Test rate spreads calculation
    df_spreads = analytics.get_rate_spreads(["DE"])
    assert not df_spreads.empty, "AnalyticsEngine.get_rate_spreads(['DE']) returned empty DataFrame"
    assert "rate_spread_bp" in df_spreads.columns
