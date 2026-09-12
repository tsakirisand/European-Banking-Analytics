import os
import sys
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db.database import Database
from src.ingestion.ecb_client import ECBClient
from src.ingestion.eurostat_client import EurostatClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("PipelineRunner")

# Target Geographies
GEOS = ["DE", "FR", "IT", "ES", "GR", "U2"]

def build_series_definitions() -> List[Dict[str, Any]]:
    """Returns exact series key definitions required by the European Banking Analytics specification."""
    series_list = []

    # 1. ECB Key Interest Rates (FM)
    series_list.extend([
        {
            "dataset_code": "FM",
            "series_key": "FM.B.U2.EUR.4F.KR.DFR.LEV",
            "indicator_name": "ECB Deposit Facility Rate",
            "geo": "U2",
            "frequency": "B",
            "unit": "% per annum",
            "description": "ECB Deposit Facility Rate (DFR) set by Governing Council"
        },
        {
            "dataset_code": "FM",
            "series_key": "FM.B.U2.EUR.4F.KR.MRR_FR.LEV",
            "indicator_name": "ECB Main Refinancing Operations Rate",
            "geo": "U2",
            "frequency": "B",
            "unit": "% per annum",
            "description": "ECB Main Refinancing Operations (MRO) Fixed Rate"
        },
        {
            "dataset_code": "FM",
            "series_key": "FM.B.U2.EUR.4F.KR.MLFR.LEV",
            "indicator_name": "ECB Marginal Lending Facility Rate",
            "geo": "U2",
            "frequency": "B",
            "unit": "% per annum",
            "description": "ECB Marginal Lending Facility Rate (MLFR)"
        }
    ])

    # 2. ECB MFI Interest Rates (MIR) for target countries
    for g in GEOS:
        series_list.extend([
            {
                "dataset_code": "MIR",
                "series_key": f"MIR.M.{g}.B.A2C.A.R.A.2250.EUR.N",
                "indicator_name": f"Mortgage Lending Rate - {g}",
                "geo": g,
                "frequency": "M",
                "unit": "% per annum",
                "description": "MFI interest rate for lending for house purchase to households"
            },
            {
                "dataset_code": "MIR",
                "series_key": f"MIR.M.{g}.B.A2B.A.R.A.2250.EUR.N",
                "indicator_name": f"Corporate Lending Rate - {g}",
                "geo": g,
                "frequency": "M",
                "unit": "% per annum",
                "description": "MFI interest rate for lending to non-financial corporations"
            },
            {
                "dataset_code": "MIR",
                "series_key": f"MIR.M.{g}.B.L21.A.R.A.2250.EUR.N",
                "indicator_name": f"Household Deposit Rate - {g}",
                "geo": g,
                "frequency": "M",
                "unit": "% per annum",
                "description": "MFI interest rate for household deposits with agreed maturity"
            },
            {
                "dataset_code": "MIR",
                "series_key": f"MIR.M.{g}.B.L22.A.R.A.2250.EUR.N",
                "indicator_name": f"Corporate Deposit Rate - {g}",
                "geo": g,
                "frequency": "M",
                "unit": "% per annum",
                "description": "MFI interest rate for corporate deposits with agreed maturity"
            }
        ])

    # 3. ECB Balance Sheet Items (BSI)
    for g in ["U2"]:
        series_list.extend([
            {
                "dataset_code": "BSI",
                "series_key": f"BSI.M.{g}.Y.U.A20.A.1.U2.2250.Z01.E",
                "indicator_name": f"Household Housing Loans Stock - {g}",
                "geo": g,
                "frequency": "M",
                "unit": "EUR Million",
                "description": "Outstanding stock of MFI loans to households for house purchase"
            },
            {
                "dataset_code": "BSI",
                "series_key": f"BSI.M.{g}.Y.U.A20.A.1.U2.2240.Z01.E",
                "indicator_name": f"Consumer Credit Stock - {g}",
                "geo": g,
                "frequency": "M",
                "unit": "EUR Million",
                "description": "Outstanding stock of MFI consumer credit loans to households"
            },
            {
                "dataset_code": "BSI",
                "series_key": f"BSI.M.{g}.Y.U.A22.A.1.U2.2250.Z01.E",
                "indicator_name": f"Corporate Loans Stock - {g}",
                "geo": g,
                "frequency": "M",
                "unit": "EUR Million",
                "description": "Outstanding stock of MFI loans to non-financial corporations"
            }
        ])

    # 4. ECB Bank Lending Survey (BLS)
    for g in ["DE", "FR", "IT", "ES", "U2"]:
        series_list.append({
            "dataset_code": "BLS",
            "series_key": f"BLS.Q.{g}.ALL.BC.E.LE.B3.ST.S.FNET",
            "indicator_name": f"Credit Standards Enterprises Net Percentage - {g}",
            "geo": g,
            "frequency": "Q",
            "unit": "Net Percentage",
            "description": "BLS Net percentage of banks reporting tightening credit standards for enterprise loans"
        })

    return series_list

def run_pipeline(db_path: str = "european_banking.db"):
    pipeline_run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    logger.info(f"Starting European Banking Analytics Ingestion Pipeline. Run ID: {pipeline_run_id}")

    db = Database(db_path)
    ecb_client = ECBClient()
    eurostat_client = EurostatClient()

    # 1. Register Datasets Catalog
    db.register_dataset("FM", "ECB", "Financial Market Statistics (Key Interest Rates)", "https://data-api.ecb.europa.eu/service/data/FM")
    db.register_dataset("MIR", "ECB", "MFI Interest Rate Statistics", "https://data-api.ecb.europa.eu/service/data/MIR")
    db.register_dataset("BSI", "ECB", "Balance Sheet Items Statistics", "https://data-api.ecb.europa.eu/service/data/BSI")
    db.register_dataset("CBD2", "ECB", "Consolidated Banking Data", "https://data-api.ecb.europa.eu/service/data/CBD2")
    db.register_dataset("BLS", "ECB", "Bank Lending Survey", "https://data-api.ecb.europa.eu/service/data/BLS")
    db.register_dataset("nama_10_gdp", "Eurostat", "GDP and Main Components", "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10_gdp")
    db.register_dataset("nama_10_pc", "Eurostat", "GDP Per Capita", "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10_pc")
    db.register_dataset("demo_gind", "Eurostat", "Population Change & Balance", "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_gind")
    db.register_dataset("prc_hicp_manr", "Eurostat", "HICP Monthly Inflation Rate", "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_manr")
    db.register_dataset("nasq_10_nf_tr", "Eurostat", "Household Disposable Income", "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nasq_10_nf_tr")

    # 2. Register Series & Ingest ECB Series
    series_defs = build_series_definitions()
    total_ingested = 0

    for sdef in series_defs:
        start_time = time.time()
        dataset_code = sdef["dataset_code"]
        series_key = sdef["series_key"]

        db.register_series(
            series_key=series_key,
            dataset_code=dataset_code,
            indicator_name=sdef["indicator_name"],
            geo=sdef["geo"],
            frequency=sdef["frequency"],
            unit=sdef["unit"],
            description=sdef["description"]
        )

        # Extract dataset portion for ECB URL call
        # Series key in ECB API URL drops the dataset prefix if embedded
        api_key = series_key
        if series_key.startswith(f"{dataset_code}."):
            api_key = series_key[len(dataset_code) + 1:]

        logger.info(f"Fetching ECB series: {dataset_code} -> {api_key}")
        observations = ecb_client.fetch_series(dataset_code, api_key)
        
        exec_duration = round(time.time() - start_time, 3)
        if observations:
            count = db.insert_observations(observations)
            total_ingested += count
            db.log_audit(pipeline_run_id, dataset_code, series_key, count, "SUCCESS", exec_time=exec_duration)
            logger.info(f"Successfully ingested {count} observations for {series_key} ({exec_duration}s)")
        else:
            db.log_audit(pipeline_run_id, dataset_code, series_key, 0, "WARNING", "No observations returned", exec_duration)
            logger.warning(f"No observations ingested for {series_key}")

    # 3. Register & Ingest Eurostat Datasets
    eurostat_queries = [
        {"dataset": "nama_10_gdp", "params": "unit=CP_MEUR&na_item=B1GQ", "indicator": "Gross Domestic Product (Current Prices)", "unit": "EUR Million", "freq": "A"},
        {"dataset": "nama_10_pc", "params": "unit=CP_EUR_HAB&na_item=B1GQ", "indicator": "GDP Per Capita (Current Prices)", "unit": "EUR per inhabitant", "freq": "A"},
        {"dataset": "demo_gind", "params": "indic_de=JAN", "indicator": "Population on 1 January", "unit": "Persons", "freq": "A"},
        {"dataset": "prc_hicp_manr", "params": "coicop=CP00", "indicator": "HICP Monthly Annual Rate of Change (Inflation)", "unit": "% change", "freq": "M"},
        {"dataset": "nasq_10_nf_tr", "params": "direct=PAID&na_item=B6G", "indicator": "Household Disposable Income", "unit": "EUR Million", "freq": "Q"}
    ]

    for target_geo in ["DE", "FR", "IT", "ES", "GR"]:
        for eq in eurostat_queries:
            start_time = time.time()
            dataset_code = eq["dataset"]
            query_params = f"{eq['params']}&geo={target_geo}"
            series_key = f"{dataset_code}:{query_params}"

            db.register_series(
                series_key=series_key,
                dataset_code=dataset_code,
                indicator_name=f"{eq['indicator']} - {target_geo}",
                geo=target_geo,
                frequency=eq["freq"],
                unit=eq["unit"],
                description=f"Eurostat dataset {dataset_code} for {target_geo}"
            )

            logger.info(f"Fetching Eurostat dataset: {dataset_code} ({target_geo})")
            obs = eurostat_client.fetch_dataset(dataset_code, query_params, target_geo, eq["freq"], eq["unit"])
            exec_duration = round(time.time() - start_time, 3)

            if obs:
                count = db.insert_observations(obs)
                total_ingested += count
                db.log_audit(pipeline_run_id, dataset_code, series_key, count, "SUCCESS", exec_time=exec_duration)
                logger.info(f"Successfully ingested {count} observations for Eurostat {dataset_code} ({target_geo}) ({exec_duration}s)")
            else:
                db.log_audit(pipeline_run_id, dataset_code, series_key, 0, "WARNING", "No observations returned", exec_duration)

    summary = db.fetch_summary_stats()
    logger.info(f"=== Pipeline Ingestion Complete ===")
    logger.info(f"Run ID: {pipeline_run_id}")
    logger.info(f"Total Observations in DB: {summary['total_observations']}")
    logger.info(f"Total Series in Catalog: {summary['total_series']}")
    logger.info(f"Total Datasets: {summary['total_datasets']}")
    logger.info(f"Covered Geographies: {', '.join(summary['geographies'])}")

if __name__ == "__main__":
    run_pipeline()
