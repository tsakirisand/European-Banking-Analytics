import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("Database")

class Database:
    def __init__(self, db_path: str = "european_banking.db"):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            with self.get_connection() as conn:
                conn.executescript(schema_sql)
                conn.commit()
            logger.info("Database schema initialized successfully.")

    def register_dataset(self, dataset_code: str, source_agency: str, dataset_name: str, base_url: str, description: str = ""):
        sql = """
        INSERT OR REPLACE INTO datasets (dataset_code, source_agency, dataset_name, base_url, description)
        VALUES (?, ?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            conn.execute(sql, (dataset_code, source_agency, dataset_name, base_url, description))
            conn.commit()

    def register_series(self, series_key: str, dataset_code: str, indicator_name: str, geo: str, frequency: str, unit: str, description: str = ""):
        sql = """
        INSERT OR REPLACE INTO series_catalog (series_key, dataset_code, indicator_name, geo, frequency, unit, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            conn.execute(sql, (series_key, dataset_code, indicator_name, geo, frequency, unit, description))
            conn.commit()

    def insert_observations(self, observations: List[Dict[str, Any]]) -> int:
        if not observations:
            return 0
        
        sql = """
        INSERT OR REPLACE INTO economic_observations 
        (observation_id, dataset_code, series_key, geo, frequency, period, period_date, obs_value, unit, retrieval_timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        records = []
        for obs in observations:
            obs_id = f"{obs['dataset_code']}:{obs['series_key']}:{obs['period']}"
            records.append((
                obs_id,
                obs['dataset_code'],
                obs['series_key'],
                obs['geo'],
                obs['frequency'],
                obs['period'],
                obs.get('period_date'),
                obs['obs_value'],
                obs.get('unit', ''),
                obs.get('retrieval_timestamp', datetime.utcnow().isoformat())
            ))

        with self.get_connection() as conn:
            conn.executemany(sql, records)
            conn.commit()
        return len(records)

    def log_audit(self, run_id: str, dataset_code: str, series_key: Optional[str], records: int, status: str, error_msg: str = "", exec_time: float = 0.0):
        sql = """
        INSERT INTO ingestion_audit (pipeline_run_id, dataset_code, series_key, records_ingested, status, error_message, execution_time_seconds)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self.get_connection() as conn:
            conn.execute(sql, (run_id, dataset_code, series_key, records, status, error_msg, exec_time))
            conn.commit()

    def fetch_summary_stats(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cur = conn.cursor()
            total_obs = cur.execute("SELECT COUNT(*) FROM economic_observations").fetchone()[0]
            total_series = cur.execute("SELECT COUNT(*) FROM series_catalog").fetchone()[0]
            total_datasets = cur.execute("SELECT COUNT(*) FROM datasets").fetchone()[0]
            geos = [row[0] for row in cur.execute("SELECT DISTINCT geo FROM series_catalog").fetchall()]
            return {
                "total_observations": total_obs,
                "total_series": total_series,
                "total_datasets": total_datasets,
                "geographies": geos
            }
