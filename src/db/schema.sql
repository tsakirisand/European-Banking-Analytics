-- European Banking Analytics Database Schema

CREATE TABLE IF NOT EXISTS datasets (
    dataset_code VARCHAR(32) PRIMARY KEY,
    source_agency VARCHAR(32) NOT NULL, -- 'ECB' or 'Eurostat'
    dataset_name VARCHAR(255) NOT NULL,
    base_url VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS series_catalog (
    series_key VARCHAR(128) PRIMARY KEY,
    dataset_code VARCHAR(32) NOT NULL REFERENCES datasets(dataset_code),
    indicator_name VARCHAR(255) NOT NULL,
    geo VARCHAR(10) NOT NULL, -- DE, FR, IT, ES, GR, U2
    frequency VARCHAR(5) NOT NULL, -- M, Q, A
    unit VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS economic_observations (
    observation_id VARCHAR(160) PRIMARY KEY, -- Hash or dataset_code:series_key:period
    dataset_code VARCHAR(32) NOT NULL,
    series_key VARCHAR(128) NOT NULL,
    geo VARCHAR(10) NOT NULL,
    frequency VARCHAR(5) NOT NULL,
    period VARCHAR(15) NOT NULL, -- e.g. 2023-01, 2023-Q1, 2023
    period_date DATE, -- Normalized ISO date
    obs_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(50),
    retrieval_timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (series_key) REFERENCES series_catalog(series_key)
);

CREATE TABLE IF NOT EXISTS ingestion_audit (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_run_id VARCHAR(64) NOT NULL,
    dataset_code VARCHAR(32) NOT NULL,
    series_key VARCHAR(128),
    records_ingested INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL, -- 'SUCCESS', 'FAILED', 'WARNING'
    error_message TEXT,
    execution_time_seconds DOUBLE PRECISION,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_obs_series_period ON economic_observations(series_key, period);
CREATE INDEX IF NOT EXISTS idx_obs_dataset_geo ON economic_observations(dataset_code, geo);
