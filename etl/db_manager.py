import os
import sqlite3
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from config.countries import EUROPEAN_COUNTRIES
from config.data_dictionary import DATASETS, INDICATORS
from src.ingestion.validator import normalize_period_to_date

logger = logging.getLogger("DBManager")

class DBManager:
    def __init__(self, db_path: str = "european_banking_star.db"):
        self.db_path = db_path
        self._known_date_keys = set()
        self._init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        schema_path = os.path.join(os.path.dirname(__file__), "..", "sql", "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            with self.get_connection() as conn:
                conn.executescript(schema_sql)
                conn.commit()
            logger.info("Star Schema database initialized successfully.")
        
        self.seed_dimensions()

    def seed_dimensions(self):
        with self.get_connection() as conn:
            # 1. Seed dim_source
            for source_code, data in DATASETS.items():
                conn.execute("""
                INSERT OR REPLACE INTO dim_source (source_code, agency_name, base_url, doc_url)
                VALUES (?, ?, ?, ?)
                """, (source_code, data["agency"], data["base_url"], data["doc_url"]))

            # 2. Seed dim_country
            for country_code, data in EUROPEAN_COUNTRIES.items():
                conn.execute("""
                INSERT OR REPLACE INTO dim_country (country_code, country_name, region, is_ea, is_eu, ea_entry_year)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (country_code, data["name"], data["region"], 1 if data["is_ea"] else 0, 1 if data["is_eu"] else 0, data.get("ea_entry_year")))

            # 3. Seed dim_indicator
            for ind_code, data in INDICATORS.items():
                conn.execute("""
                INSERT OR REPLACE INTO dim_indicator (indicator_code, indicator_name, category, unit, frequency, source_code, series_key_template, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (ind_code, data["name"], data["category"], data["unit"], data["frequency"], data["dataset_code"], data.get("series_template") or data.get("series_key"), data["description"]))

            conn.commit()
            logger.info("Star Schema dimensions seeded successfully.")

    def ensure_date_dimension(self, date_key: str, frequency: str):
        if date_key in self._known_date_keys:
            return
        p_date = normalize_period_to_date(date_key, frequency)
        year = int(date_key[:4]) if len(date_key) >= 4 and date_key[:4].isdigit() else 2000
        quarter = None
        month = None
        if "Q" in date_key:
            quarter = int(date_key.split("Q")[-1])
        elif "-" in date_key and len(date_key.split("-")[1]) == 2:
            month = int(date_key.split("-")[1])

        sql = """
        INSERT OR REPLACE INTO dim_date (date_key, year, quarter, month, period_date, frequency)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            conn.execute(sql, (date_key, year, quarter, month, p_date, frequency))
            conn.commit()
        self._known_date_keys.add(date_key)

    def insert_fact_records(self, table_name: str, records: List[Dict[str, Any]]) -> int:
        if not records:
            return 0

        valid_tables = {
            "fact_interest_rates",
            "fact_loans_deposits",
            "fact_banking_sector",
            "fact_lending_survey",
            "fact_macro"
        }
        if table_name not in valid_tables:
            raise ValueError(f"Invalid table name: {table_name}")

        sql = f"""
        INSERT OR REPLACE INTO {table_name} 
        (fact_id, country_code, indicator_code, date_key, obs_value, unit, retrieval_timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        data_rows = []
        retrieval_ts = datetime.now(timezone.utc).isoformat()

        for rec in records:
            fact_id = f"{rec['country_code']}:{rec['indicator_code']}:{rec['date_key']}"
            self.ensure_date_dimension(rec['date_key'], rec.get('frequency', 'M'))
            data_rows.append((
                fact_id,
                rec['country_code'],
                rec['indicator_code'],
                rec['date_key'],
                rec['obs_value'],
                rec.get('unit', ''),
                rec.get('retrieval_timestamp', retrieval_ts)
            ))

        with self.get_connection() as conn:
            conn.executemany(sql, data_rows)
            conn.commit()

        return len(data_rows)

    def log_validation(self, run_id: str, stage: str, rule_name: str, status: str, record_id: str = "", details: str = ""):
        sql = """
        INSERT INTO validation_logs (pipeline_run_id, stage, rule_name, status, record_identifier, details)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            conn.execute(sql, (run_id, stage, rule_name, status, record_id, details))
            conn.commit()
