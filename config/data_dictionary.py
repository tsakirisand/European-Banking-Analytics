"""
Data Dictionary for European Banking Analytics
Central metadata repository for all indicators, exact series key templates, units, frequencies, and documentation URLs.
"""

from typing import Dict, Any

DATASETS: Dict[str, Dict[str, Any]] = {
    "FM": {
        "agency": "ECB",
        "name": "Financial Market Statistics (Key Interest Rates)",
        "base_url": "https://data-api.ecb.europa.eu/service/data/FM",
        "doc_url": "https://data.ecb.europa.eu/help/api/overview"
    },
    "MIR": {
        "agency": "ECB",
        "name": "MFI Interest Rate Statistics",
        "base_url": "https://data-api.ecb.europa.eu/service/data/MIR",
        "doc_url": "https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/bank_interest_rates/mfi_interest_rates/html/index.en.html"
    },
    "BSI": {
        "agency": "ECB",
        "name": "Balance Sheet Items Statistics",
        "base_url": "https://data-api.ecb.europa.eu/service/data/BSI",
        "doc_url": "https://www.ecb.europa.eu/stats/financial_corporations/monetary_financial_institutions/balance_sheets/html/index.en.html"
    },
    "CBD2": {
        "agency": "ECB",
        "name": "Consolidated Banking Data",
        "base_url": "https://data-api.ecb.europa.eu/service/data/CBD2",
        "doc_url": "https://www.ecb.europa.eu/stats/financial_corporations/consolidated_banking_data/html/index.en.html"
    },
    "BLS": {
        "agency": "ECB",
        "name": "Bank Lending Survey Statistics",
        "base_url": "https://data-api.ecb.europa.eu/service/data/BLS",
        "doc_url": "https://www.ecb.europa.eu/stats/ecb_surveys/bank_lending_survey/html/index.en.html"
    },
    "nama_10_gdp": {
        "agency": "Eurostat",
        "name": "Gross Domestic Product (Annual)",
        "base_url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10_gdp",
        "doc_url": "https://ec.europa.eu/eurostat/cache/metadata/en/nama10_esms.htm"
    },
    "nama_10_pc": {
        "agency": "Eurostat",
        "name": "GDP Per Capita (Annual)",
        "base_url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10_pc",
        "doc_url": "https://ec.europa.eu/eurostat/cache/metadata/en/nama10_esms.htm"
    },
    "demo_gind": {
        "agency": "Eurostat",
        "name": "Population on 1 January",
        "base_url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_gind",
        "doc_url": "https://ec.europa.eu/eurostat/cache/metadata/en/demo_gind_esms.htm"
    },
    "prc_hicp_manr": {
        "agency": "Eurostat",
        "name": "HICP Monthly Inflation Rate",
        "base_url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_manr",
        "doc_url": "https://ec.europa.eu/eurostat/cache/metadata/en/prc_hicp_esms.htm"
    },
    "nasq_10_nf_tr": {
        "agency": "Eurostat",
        "name": "Household Disposable Income",
        "base_url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nasq_10_nf_tr",
        "doc_url": "https://ec.europa.eu/eurostat/cache/metadata/en/nasq_10_esms.htm"
    }
}

INDICATORS: Dict[str, Dict[str, Any]] = {
    # Monetary Policy
    "ECB_DFR": {
        "category": "Monetary Policy",
        "name": "Deposit Facility Rate",
        "unit": "% per annum",
        "frequency": "B",
        "series_key": "FM.B.U2.EUR.4F.KR.DFR.LEV",
        "dataset_code": "FM",
        "description": "ECB Deposit Facility Rate set by Governing Council"
    },
    "ECB_MRO": {
        "category": "Monetary Policy",
        "name": "Main Refinancing Operations Rate",
        "unit": "% per annum",
        "frequency": "B",
        "series_key": "FM.B.U2.EUR.4F.KR.MRR_FR.LEV",
        "dataset_code": "FM",
        "description": "ECB Main Refinancing Operations fixed rate"
    },
    "ECB_MLFR": {
        "category": "Monetary Policy",
        "name": "Marginal Lending Facility Rate",
        "unit": "% per annum",
        "frequency": "B",
        "series_key": "FM.B.U2.EUR.4F.KR.MLFR.LEV",
        "dataset_code": "FM",
        "description": "ECB Marginal Lending Facility Rate"
    },
    # Interest Rates
    "MIR_MORTGAGE": {
        "category": "Interest Rates",
        "name": "Mortgage Lending Rate",
        "unit": "% per annum",
        "frequency": "M",
        "series_template": "MIR.M.{geo}.B.A2C.A.R.A.2250.EUR.N",
        "dataset_code": "MIR",
        "description": "MFI interest rate for lending for house purchase to households"
    },
    "MIR_CORPORATE": {
        "category": "Interest Rates",
        "name": "Corporate Lending Rate",
        "unit": "% per annum",
        "frequency": "M",
        "series_template": "MIR.M.{geo}.B.A2B.A.R.A.2250.EUR.N",
        "dataset_code": "MIR",
        "description": "MFI interest rate for lending to non-financial corporations"
    },
    "MIR_HH_DEPOSIT": {
        "category": "Interest Rates",
        "name": "Household Deposit Rate",
        "unit": "% per annum",
        "frequency": "M",
        "series_template": "MIR.M.{geo}.B.L21.A.R.A.2250.EUR.N",
        "dataset_code": "MIR",
        "description": "MFI interest rate for household deposits with agreed maturity"
    },
    "MIR_CORP_DEPOSIT": {
        "category": "Interest Rates",
        "name": "Corporate Deposit Rate",
        "unit": "% per annum",
        "frequency": "M",
        "series_template": "MIR.M.{geo}.B.L22.A.R.A.2250.EUR.N",
        "dataset_code": "MIR",
        "description": "MFI interest rate for corporate deposits with agreed maturity"
    },
    # Balance Sheet / Credit
    "BSI_HOUSING_LOANS": {
        "category": "Loans & Credit",
        "name": "Housing Loans Outstanding Stock",
        "unit": "EUR Million",
        "frequency": "M",
        "series_template": "BSI.M.{geo}.Y.U.A20.A.1.U2.2250.Z01.E",
        "dataset_code": "BSI",
        "description": "Outstanding MFI housing loans stock to households"
    },
    "BSI_CONSUMER_CREDIT": {
        "category": "Loans & Credit",
        "name": "Consumer Credit Outstanding Stock",
        "unit": "EUR Million",
        "frequency": "M",
        "series_template": "BSI.M.{geo}.Y.U.A20.A.1.U2.2240.Z01.E",
        "dataset_code": "BSI",
        "description": "Outstanding MFI consumer credit stock to households"
    },
    "BSI_CORP_LOANS": {
        "category": "Loans & Credit",
        "name": "Corporate Loans Outstanding Stock",
        "unit": "EUR Million",
        "frequency": "M",
        "series_template": "BSI.M.{geo}.Y.U.A22.A.1.U2.2250.Z01.E",
        "dataset_code": "BSI",
        "description": "Outstanding MFI loans to non-financial corporations"
    },
    # Bank Lending Survey
    "BLS_ENTERPRISE_STANDARDS": {
        "category": "Lending Survey",
        "name": "Credit Standards Enterprises (Net %)",
        "unit": "Net Percentage",
        "frequency": "Q",
        "series_template": "BLS.Q.{geo}.ALL.BC.E.LE.B3.ST.S.FNET",
        "dataset_code": "BLS",
        "description": "BLS net percentage of banks reporting tightening credit standards for enterprises"
    },
    # Macroeconomics
    "EUROSTAT_GDP": {
        "category": "Macroeconomics",
        "name": "Gross Domestic Product (GDP)",
        "unit": "EUR Million",
        "frequency": "A",
        "dataset_code": "nama_10_gdp",
        "query_params": "unit=CP_MEUR&na_item=B1GQ",
        "description": "Gross domestic product at current market prices"
    },
    "EUROSTAT_GDP_PC": {
        "category": "Macroeconomics",
        "name": "GDP Per Capita",
        "unit": "EUR / inhabitant",
        "frequency": "A",
        "dataset_code": "nama_10_pc",
        "query_params": "unit=CP_EUR_HAB&na_item=B1GQ",
        "description": "GDP per inhabitant at current market prices"
    },
    "EUROSTAT_POP": {
        "category": "Macroeconomics",
        "name": "Population on 1 January",
        "unit": "Persons",
        "frequency": "A",
        "dataset_code": "demo_gind",
        "query_params": "indic_de=JAN",
        "description": "Total population on 1 January"
    },
    "EUROSTAT_HICP": {
        "category": "Macroeconomics",
        "name": "HICP Monthly Inflation Rate",
        "unit": "% change",
        "frequency": "M",
        "dataset_code": "prc_hicp_manr",
        "query_params": "coicop=CP00",
        "description": "Harmonised Index of Consumer Prices monthly annual rate of change"
    },
    "EUROSTAT_DISP_INC": {
        "category": "Macroeconomics",
        "name": "Household Disposable Income",
        "unit": "EUR Million",
        "frequency": "Q",
        "dataset_code": "nasq_10_nf_tr",
        "query_params": "direct=PAID&na_item=B6G",
        "description": "Gross disposable income of households"
    },
    # Consolidated Banking Data (CBD2) - Profitability & Risk
    "CBD2_ROE": {
        "category": "Profitability",
        "name": "Return on Equity (ROE)",
        "unit": "%",
        "frequency": "A",
        "dataset_code": "CBD2",
        "description": "Consolidated Banking Data Return on Equity"
    },
    "CBD2_ROA": {
        "category": "Profitability",
        "name": "Return on Assets (ROA)",
        "unit": "%",
        "frequency": "A",
        "dataset_code": "CBD2",
        "description": "Consolidated Banking Data Return on Assets"
    },
    "CBD2_NPL": {
        "category": "Risk",
        "name": "Non-Performing Loans Ratio (NPL)",
        "unit": "%",
        "frequency": "A",
        "dataset_code": "CBD2",
        "description": "Non-performing loans as share of total gross loans"
    },
    "CBD2_CET1": {
        "category": "Risk",
        "name": "Common Equity Tier 1 Ratio (CET1)",
        "unit": "%",
        "frequency": "A",
        "dataset_code": "CBD2",
        "description": "Common Equity Tier 1 capital ratio"
    },
    "CBD2_LCR": {
        "category": "Risk",
        "name": "Liquidity Coverage Ratio (LCR)",
        "unit": "%",
        "frequency": "A",
        "dataset_code": "CBD2",
        "description": "Liquidity Coverage Ratio for commercial banks"
    }
}
