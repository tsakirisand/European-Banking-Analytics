# European Banking Analytics - Exact Series Catalog

This document registers every exact dataset code and series key used in the **European Banking Analytics** platform, detailing source endpoints, frequencies, geographies, and indicator definitions.

---

## 1. ECB SDMX REST API Datasets

**Base URL**: `https://data-api.ecb.europa.eu/service/data/`

### 1.1 Financial Market Statistics (`FM`) - Key Interest Rates
*Official ECB Policy Interest Rates set by the Governing Council.*

| Indicator Name | Exact Series Key | Geo | Freq | Unit | Endpoint |
|---|---|---|---|---|---|
| ECB Deposit Facility Rate (DFR) | `FM.B.U2.EUR.4F.KR.DFR.LEV` | U2 | B | % p.a. | `https://data-api.ecb.europa.eu/service/data/FM/B.U2.EUR.4F.KR.DFR.LEV` |
| ECB Main Refinancing Operations (MRO) | `FM.B.U2.EUR.4F.KR.MRR_FR.LEV` | U2 | B | % p.a. | `https://data-api.ecb.europa.eu/service/data/FM/B.U2.EUR.4F.KR.MRR_FR.LEV` |
| ECB Marginal Lending Facility (MLFR) | `FM.B.U2.EUR.4F.KR.MLFR.LEV` | U2 | B | % p.a. | `https://data-api.ecb.europa.eu/service/data/FM/B.U2.EUR.4F.KR.MLFR.LEV` |

---

### 1.2 MFI Interest Rate Statistics (`MIR`)
*Interest rates charged and paid by Monetary Financial Institutions (MFIs) on loans and deposits.*

| Indicator Name | Exact Series Key Pattern | Geo Scope | Freq | Unit |
|---|---|---|---|---|
| Mortgage Rates (House Purchase) | `MIR.M.<GEO>.B.A2C.A.R.A.2250.EUR.N` | DE, FR, IT, ES, GR, U2 | Monthly (M) | % p.a. |
| Corporate Lending Rates | `MIR.M.<GEO>.B.A2B.A.R.A.2250.EUR.N` | DE, FR, IT, ES, GR, U2 | Monthly (M) | % p.a. |
| Household Deposit Rates | `MIR.M.<GEO>.B.L21.A.R.A.2250.EUR.N` | DE, FR, IT, ES, GR, U2 | Monthly (M) | % p.a. |
| Corporate Deposit Rates | `MIR.M.<GEO>.B.L22.A.R.A.2250.EUR.N` | DE, FR, IT, ES, GR, U2 | Monthly (M) | % p.a. |

---

### 1.3 Balance Sheet Items (`BSI`)
*Monetary Financial Institutions (MFI) balance sheet stocks, credit aggregates, and deposit aggregates.*

| Indicator Name | Exact Series Key | Geo | Freq | Unit |
|---|---|---|---|---|
| Housing Loans Stock | `BSI.M.U2.Y.U.A20.A.1.U2.2250.Z01.E` | U2 | Monthly (M) | EUR Million |
| Consumer Credit Stock | `BSI.M.U2.Y.U.A20.A.1.U2.2240.Z01.E` | U2 | Monthly (M) | EUR Million |
| Corporate Loans Stock | `BSI.M.U2.Y.U.A22.A.1.U2.2250.Z01.E` | U2 | Monthly (M) | EUR Million |

---

### 1.4 Bank Lending Survey (`BLS`)
*Qualitative survey metrics on bank credit standards, terms and conditions, and loan demand.*

| Indicator Name | Exact Series Key Pattern | Geo Scope | Freq | Unit |
|---|---|---|---|---|
| Enterprise Credit Standards Net % | `BLS.Q.<GEO>.ALL.BC.E.LE.B3.ST.S.FNET` | DE, FR, IT, ES, U2 | Quarterly (Q) | Net % |

---

## 2. Eurostat Dissemination API Datasets

**Base URL**: `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/`

| Dataset Code | Indicator Name | URL Query Parameters | Geo Scope | Freq | Unit |
|---|---|---|---|---|---|
| `nama_10_gdp` | Gross Domestic Product | `unit=CP_MEUR&na_item=B1GQ&geo=<GEO>` | DE, FR, IT, ES, GR | Annual (A) | EUR Million |
| `nama_10_pc` | GDP Per Capita | `unit=CP_EUR_HAB&na_item=B1GQ&geo=<GEO>` | DE, FR, IT, ES, GR | Annual (A) | EUR / Inhabitant |
| `demo_gind` | Population on 1 January | `indic_de=JAN&geo=<GEO>` | DE, FR, IT, ES, GR | Annual (A) | Persons |
| `prc_hicp_manr` | HICP Monthly Inflation Rate | `coicop=CP00&geo=<GEO>` | DE, FR, IT, ES, GR | Monthly (M) | % Change |
| `nasq_10_nf_tr` | Household Disposable Income | `direct=PAID&na_item=B6G&geo=<GEO>` | DE, FR, IT, ES, GR | Quarterly (Q) | EUR Million |

---

## 3. Data Governance & Frequency Rules

1. **No Mixed Frequencies**: Monthly (`M`), Quarterly (`Q`), Annual (`A`), and Business-daily (`B`) observations retain their standard frequency tags in `economic_observations.frequency`.
2. **Normalized Dates**: Period strings are parsed to explicit ISO start dates (`YYYY-MM-DD`) in `period_date`.
3. **Auditability**: Ingestion runs log total observations, duration, status, and error messages to `ingestion_audit`.
