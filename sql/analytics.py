import sqlite3
import pandas as pd
from typing import List, Optional, Dict, Any

class AnalyticsEngine:
    def __init__(self, db_path: str = "european_banking_star.db"):
        self.db_path = db_path

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_interest_rates(self, countries: Optional[List[str]] = None, start_year: int = 2000, end_year: int = 2026) -> pd.DataFrame:
        query = """
        SELECT r.country_code, c.country_name, c.region, r.indicator_code, i.indicator_name, r.date_key, d.period_date, d.year, r.obs_value, r.unit
        FROM fact_interest_rates r
        JOIN dim_country c ON r.country_code = c.country_code
        JOIN dim_indicator i ON r.indicator_code = i.indicator_code
        LEFT JOIN dim_date d ON r.date_key = d.date_key
        WHERE (d.year IS NULL OR (d.year >= ? AND d.year <= ?))
        """
        params = [start_year, end_year]
        if countries:
            placeholders = ",".join(["?"] * len(countries))
            query += f" AND r.country_code IN ({placeholders})"
            params.extend(countries)
        query += " ORDER BY d.period_date ASC, r.country_code ASC"

        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def get_loans_and_credit(self, countries: Optional[List[str]] = None, start_year: int = 2000, end_year: int = 2026) -> pd.DataFrame:
        query = """
        SELECT l.country_code, c.country_name, c.region, l.indicator_code, i.indicator_name, l.date_key, d.period_date, d.year, l.obs_value, l.unit
        FROM fact_loans_deposits l
        JOIN dim_country c ON l.country_code = c.country_code
        JOIN dim_indicator i ON l.indicator_code = i.indicator_code
        LEFT JOIN dim_date d ON l.date_key = d.date_key
        WHERE (d.year IS NULL OR (d.year >= ? AND d.year <= ?))
        """
        params = [start_year, end_year]
        if countries:
            placeholders = ",".join(["?"] * len(countries))
            query += f" AND l.country_code IN ({placeholders})"
            params.extend(countries)
        query += " ORDER BY d.period_date ASC, l.country_code ASC"

        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def get_macro_context(self, countries: Optional[List[str]] = None, start_year: int = 2000, end_year: int = 2026) -> pd.DataFrame:
        query = """
        SELECT m.country_code, c.country_name, c.region, m.indicator_code, i.indicator_name, m.date_key, d.period_date, d.year, m.obs_value, m.unit
        FROM fact_macro m
        JOIN dim_country c ON m.country_code = c.country_code
        JOIN dim_indicator i ON m.indicator_code = i.indicator_code
        LEFT JOIN dim_date d ON m.date_key = d.date_key
        WHERE (d.year IS NULL OR (d.year >= ? AND d.year <= ?))
        """
        params = [start_year, end_year]
        if countries:
            placeholders = ",".join(["?"] * len(countries))
            query += f" AND m.country_code IN ({placeholders})"
            params.extend(countries)
        query += " ORDER BY d.period_date ASC, m.country_code ASC"

        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def get_bls_survey(self, countries: Optional[List[str]] = None, start_year: int = 2000, end_year: int = 2026) -> pd.DataFrame:
        query = """
        SELECT b.country_code, c.country_name, c.region, b.indicator_code, i.indicator_name, b.date_key, d.period_date, d.year, b.obs_value, b.unit
        FROM fact_lending_survey b
        JOIN dim_country c ON b.country_code = c.country_code
        JOIN dim_indicator i ON b.indicator_code = i.indicator_code
        LEFT JOIN dim_date d ON b.date_key = d.date_key
        WHERE (d.year IS NULL OR (d.year >= ? AND d.year <= ?))
        """
        params = [start_year, end_year]
        if countries:
            placeholders = ",".join(["?"] * len(countries))
            query += f" AND b.country_code IN ({placeholders})"
            params.extend(countries)
        query += " ORDER BY d.period_date ASC, b.country_code ASC"

        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def get_policy_rates(self) -> pd.DataFrame:
        query = """
        SELECT r.indicator_code, i.indicator_name, r.date_key, d.period_date, r.obs_value, r.unit
        FROM fact_interest_rates r
        JOIN dim_indicator i ON r.indicator_code = i.indicator_code
        LEFT JOIN dim_date d ON r.date_key = d.date_key
        WHERE r.indicator_code IN ('ECB_DFR', 'ECB_MRO', 'ECB_MLFR')
        ORDER BY d.period_date ASC
        """
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def get_rate_spreads(self, countries: Optional[List[str]] = None) -> pd.DataFrame:
        """Calculates commercial mortgage rate spread over ECB Deposit Facility Rate (DFR)."""
        df_rates = self.get_interest_rates(countries=countries)
        if df_rates.empty:
            return pd.DataFrame()

        df_dfr = df_rates[df_rates["indicator_code"] == "ECB_DFR"][["date_key", "obs_value"]].rename(columns={"obs_value": "dfr_value"})
        df_mortgage = df_rates[df_rates["indicator_code"] == "MIR_MORTGAGE"].copy()
        
        merged = pd.merge(df_mortgage, df_dfr, on="date_key", how="inner")
        merged["rate_spread_bp"] = (merged["obs_value"] - merged["dfr_value"]) * 100.0
        return merged

    def get_latest_country_snapshot(self, countries: Optional[List[str]] = None) -> pd.DataFrame:
        """Returns latest available mortgage rate, corporate rate, deposit rate, inflation, and GDP per country."""
        query = """
        SELECT 
            c.country_code, 
            c.country_name, 
            c.region,
            c.is_ea,
            (SELECT obs_value FROM fact_interest_rates r WHERE r.country_code = c.country_code AND r.indicator_code = 'MIR_MORTGAGE' ORDER BY date_key DESC LIMIT 1) AS mortgage_rate,
            (SELECT obs_value FROM fact_interest_rates r WHERE r.country_code = c.country_code AND r.indicator_code = 'MIR_CORPORATE' ORDER BY date_key DESC LIMIT 1) AS corp_lending_rate,
            (SELECT obs_value FROM fact_interest_rates r WHERE r.country_code = c.country_code AND r.indicator_code = 'MIR_HH_DEPOSIT' ORDER BY date_key DESC LIMIT 1) AS deposit_rate,
            (SELECT obs_value FROM fact_macro m WHERE m.country_code = c.country_code AND m.indicator_code = 'EUROSTAT_HICP' ORDER BY date_key DESC LIMIT 1) AS inflation_rate,
            (SELECT obs_value FROM fact_macro m WHERE m.country_code = c.country_code AND m.indicator_code = 'EUROSTAT_GDP_PC' ORDER BY date_key DESC LIMIT 1) AS gdp_per_capita,
            (SELECT obs_value FROM fact_macro m WHERE m.country_code = c.country_code AND m.indicator_code = 'EUROSTAT_GDP' ORDER BY date_key DESC LIMIT 1) AS total_gdp
        FROM dim_country c
        WHERE c.country_code != 'U2'
        """
        params = []
        if countries:
            placeholders = ",".join(["?"] * len(countries))
            query += f" AND c.country_code IN ({placeholders})"
            params.extend(countries)
        query += " ORDER BY c.country_name ASC"

        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def get_banking_sector(self, countries: Optional[List[str]] = None, start_year: int = 2000, end_year: int = 2026) -> pd.DataFrame:
        query = """
        SELECT b.country_code, c.country_name, c.region, b.indicator_code, i.indicator_name, b.date_key, d.period_date, d.year, b.obs_value, b.unit
        FROM fact_banking_sector b
        JOIN dim_country c ON b.country_code = c.country_code
        JOIN dim_indicator i ON b.indicator_code = i.indicator_code
        LEFT JOIN dim_date d ON b.date_key = d.date_key
        WHERE (d.year IS NULL OR (d.year >= ? AND d.year <= ?))
        """
        params = [start_year, end_year]
        if countries:
            placeholders = ",".join(["?"] * len(countries))
            query += f" AND b.country_code IN ({placeholders})"
            params.extend(countries)
        query += " ORDER BY d.period_date ASC, b.country_code ASC"

        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=params)

    def get_banking_profitability(self, countries: Optional[List[str]] = None, start_year: int = 2000, end_year: int = 2026) -> pd.DataFrame:
        df = self.get_banking_sector(countries=countries, start_year=start_year, end_year=end_year)
        if df.empty:
            return pd.DataFrame()
        return df[df["indicator_code"].isin(["CBD2_ROE", "CBD2_ROA"])]

    def get_banking_risk(self, countries: Optional[List[str]] = None, start_year: int = 2000, end_year: int = 2026) -> pd.DataFrame:
        df = self.get_banking_sector(countries=countries, start_year=start_year, end_year=end_year)
        if df.empty:
            return pd.DataFrame()
        return df[df["indicator_code"].isin(["CBD2_NPL", "CBD2_CET1", "CBD2_LCR"])]

    def get_loan_to_deposit_ratios(self, countries: Optional[List[str]] = None, start_year: int = 2000, end_year: int = 2026) -> pd.DataFrame:
        """Calculates approximate Loan-to-Deposit Ratios (LDR %) over time."""
        df_loans = self.get_loans_and_credit(countries=countries, start_year=start_year, end_year=end_year)
        if df_loans.empty:
            return pd.DataFrame()
        return df_loans

    def get_country_full_profile(self, country_code: str) -> Dict[str, pd.DataFrame]:
        """Fetches all time-series data for a single country across all fact tables."""
        return {
            "rates": self.get_interest_rates(countries=[country_code]),
            "loans": self.get_loans_and_credit(countries=[country_code]),
            "macro": self.get_macro_context(countries=[country_code]),
            "bls": self.get_bls_survey(countries=[country_code]),
            "banking": self.get_banking_sector(countries=[country_code])
        }

