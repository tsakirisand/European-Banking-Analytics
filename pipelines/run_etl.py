import os
import sys
import time
import uuid
import logging
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from etl.db_manager import DBManager
from etl.ecb_ingestion import ECBIngestion
from etl.eurostat_ingestion import EurostatIngestion
from validation.validator import ValidatorEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ETLPipeline")

def run_full_etl(db_path: str = "european_banking_star.db"):
    run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    logger.info(f"Starting European Banking Analytics Full Star Schema ETL. Run ID: {run_id}")

    db = DBManager(db_path)
    validator = ValidatorEngine()
    ecb_etl = ECBIngestion()
    eurostat_etl = EurostatIngestion()

    total_inserted = 0

    # 1. Ingest ECB Fact Tables
    logger.info("Ingesting ECB Fact Tables...")
    ecb_tables = ecb_etl.fetch_all_ecb_indicators()
    for table_name, records in ecb_tables.items():
        if not records:
            continue
        v_res = validator.validate_batch(records)
        db.log_validation(run_id, "ECB_Ingestion", table_name, "SUMMARY", details=f"PASS: {v_res['PASS']}, FAIL: {v_res['FAIL']}, WARNING: {v_res['WARNING']}")
        
        valid_records = [r for r in records if validator.validate_record(r)[0] in ["PASS", "WARNING"]]
        cnt = db.insert_fact_records(table_name, valid_records)
        total_inserted += cnt
        logger.info(f"Ingested {cnt} records into {table_name}")

    # 2. Ingest Eurostat Macro Fact Table
    logger.info("Ingesting Eurostat Macro Fact Table...")
    macro_records = eurostat_etl.fetch_all_macro_indicators()
    if macro_records:
        v_res = validator.validate_batch(macro_records)
        db.log_validation(run_id, "Eurostat_Ingestion", "fact_macro", "SUMMARY", details=f"PASS: {v_res['PASS']}, FAIL: {v_res['FAIL']}, WARNING: {v_res['WARNING']}")
        
        valid_macro = [r for r in macro_records if validator.validate_record(r)[0] in ["PASS", "WARNING"]]
        cnt = db.insert_fact_records("fact_macro", valid_macro)
        total_inserted += cnt
        logger.info(f"Ingested {cnt} records into fact_macro")

    logger.info(f"=== Star Schema ETL Pipeline Finished ===")
    logger.info(f"Run ID: {run_id}")
    logger.info(f"Total Fact Records Inserted: {total_inserted}")

if __name__ == "__main__":
    run_full_etl()
