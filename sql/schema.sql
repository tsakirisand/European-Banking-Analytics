-- European Banking Analytics Star Schema Database DDL (PostgreSQL & SQLite Compatible)

-- Dimension Tables
CREATE TABLE IF NOT EXISTS dim_source (
    source_code VARCHAR(32) PRIMARY KEY,
    agency_name VARCHAR(128) NOT NULL,
    base_url VARCHAR(255) NOT NULL,
    doc_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_country (
    country_code VARCHAR(10) PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL, -- Western, Southern, Northern, Eastern, Aggregate
    is_ea BOOLEAN NOT NULL DEFAULT 0,
    is_eu BOOLEAN NOT NULL DEFAULT 1,
    ea_entry_year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_indicator (
    indicator_code VARCHAR(64) PRIMARY KEY,
    indicator_name VARCHAR(255) NOT NULL,
    category VARCHAR(64) NOT NULL, -- Monetary Policy, Interest Rates, Loans & Credit, Profitability, Risk, Macroeconomics
    unit VARCHAR(50) NOT NULL,
    frequency VARCHAR(5) NOT NULL, -- M, Q, A, B
    source_code VARCHAR(32) NOT NULL,
    series_key_template VARCHAR(255),
    description TEXT,
    FOREIGN KEY (source_code) REFERENCES dim_source(source_code)
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_key VARCHAR(15) PRIMARY KEY, -- e.g. '2023-01', '2023-Q1', '2023'
    year INTEGER NOT NULL,
    quarter INTEGER,
    month INTEGER,
    period_date DATE, -- ISO date YYYY-MM-DD
    frequency VARCHAR(5) NOT NULL
);

-- Fact Tables
CREATE TABLE IF NOT EXISTS fact_interest_rates (
    fact_id VARCHAR(160) PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    indicator_code VARCHAR(64) NOT NULL,
    date_key VARCHAR(15) NOT NULL,
    obs_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(50),
    retrieval_timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (country_code) REFERENCES dim_country(country_code),
    FOREIGN KEY (indicator_code) REFERENCES dim_indicator(indicator_code),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE TABLE IF NOT EXISTS fact_loans_deposits (
    fact_id VARCHAR(160) PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    indicator_code VARCHAR(64) NOT NULL,
    date_key VARCHAR(15) NOT NULL,
    obs_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(50),
    retrieval_timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (country_code) REFERENCES dim_country(country_code),
    FOREIGN KEY (indicator_code) REFERENCES dim_indicator(indicator_code),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE TABLE IF NOT EXISTS fact_banking_sector (
    fact_id VARCHAR(160) PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    indicator_code VARCHAR(64) NOT NULL,
    date_key VARCHAR(15) NOT NULL,
    obs_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(50),
    retrieval_timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (country_code) REFERENCES dim_country(country_code),
    FOREIGN KEY (indicator_code) REFERENCES dim_indicator(indicator_code),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE TABLE IF NOT EXISTS fact_lending_survey (
    fact_id VARCHAR(160) PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    indicator_code VARCHAR(64) NOT NULL,
    date_key VARCHAR(15) NOT NULL,
    obs_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(50),
    retrieval_timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (country_code) REFERENCES dim_country(country_code),
    FOREIGN KEY (indicator_code) REFERENCES dim_indicator(indicator_code),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

CREATE TABLE IF NOT EXISTS fact_macro (
    fact_id VARCHAR(160) PRIMARY KEY,
    country_code VARCHAR(10) NOT NULL,
    indicator_code VARCHAR(64) NOT NULL,
    date_key VARCHAR(15) NOT NULL,
    obs_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(50),
    retrieval_timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (country_code) REFERENCES dim_country(country_code),
    FOREIGN KEY (indicator_code) REFERENCES dim_indicator(indicator_code),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- Validation & Audit Logs
CREATE TABLE IF NOT EXISTS validation_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_run_id VARCHAR(64) NOT NULL,
    stage VARCHAR(64) NOT NULL,
    rule_name VARCHAR(128) NOT NULL,
    status VARCHAR(20) NOT NULL, -- PASS, FAIL, WARNING, UNVERIFIED
    record_identifier VARCHAR(160),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Fast Analytics Queries
CREATE INDEX IF NOT EXISTS idx_rates_country_date ON fact_interest_rates(country_code, date_key);
CREATE INDEX IF NOT EXISTS idx_loans_country_date ON fact_loans_deposits(country_code, date_key);
CREATE INDEX IF NOT EXISTS idx_banking_country_date ON fact_banking_sector(country_code, date_key);
CREATE INDEX IF NOT EXISTS idx_lending_country_date ON fact_lending_survey(country_code, date_key);
CREATE INDEX IF NOT EXISTS idx_macro_country_date ON fact_macro(country_code, date_key);
