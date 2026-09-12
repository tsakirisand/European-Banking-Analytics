import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sql.analytics import AnalyticsEngine
from dashboard.components.filters import render_sidebar_filters

st.set_page_config(
    page_title="European Banking Analytics",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for Financial UI
st.markdown("""
<style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 2.0rem;
        font-weight: 700;
        color: #0F172A;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏦 European Banking Analytics Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Cross-country financial analytics, interest rates, balance sheets, profitability, risk, and monetary policy transmission across European economies.</div>', unsafe_allow_html=True)

selected_countries, start_year, end_year = render_sidebar_filters()

analytics = AnalyticsEngine()
df_snapshot = analytics.get_latest_country_snapshot(selected_countries)

st.markdown("### Executive European Financial Overview")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card"><div class="metric-value">3.25%</div><div class="metric-label">ECB Deposit Facility Rate</div></div>', unsafe_allow_html=True)

with col2:
    if not df_snapshot.empty and "mortgage_rate" in df_snapshot:
        avg_m = df_snapshot["mortgage_rate"].dropna().mean()
        st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_m:.2f}%</div><div class="metric-label">Avg Mortgage Rate (Selected)</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-card"><div class="metric-value">3.85%</div><div class="metric-label">Avg Mortgage Rate</div></div>', unsafe_allow_html=True)

with col3:
    if not df_snapshot.empty and "corp_lending_rate" in df_snapshot:
        avg_c = df_snapshot["corp_lending_rate"].dropna().mean()
        st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_c:.2f}%</div><div class="metric-label">Avg Corporate Rate (Selected)</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="metric-card"><div class="metric-value">4.72%</div><div class="metric-label">Avg Corporate Rate</div></div>', unsafe_allow_html=True)

with col4:
    n_count = len(selected_countries) if selected_countries else 26
    st.markdown(f'<div class="metric-card"><div class="metric-value">{n_count}</div><div class="metric-label">Selected European Countries</div></div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("### Latest Country Snapshot Matrix")
if not df_snapshot.empty:
    st.dataframe(
        df_snapshot.rename(columns={
            "country_code": "Code",
            "country_name": "Country Name",
            "region": "Region",
            "is_ea": "Euro Area",
            "mortgage_rate": "Mortgage Rate (%)",
            "corp_lending_rate": "Corp Rate (%)",
            "deposit_rate": "Deposit Rate (%)",
            "inflation_rate": "Inflation (%)",
            "gdp_per_capita": "GDP Per Capita (€)"
        }),
        use_container_width=True
    )
else:
    st.info("Select countries from the sidebar to display financial metrics.")

st.markdown("---")
st.markdown("### Platform Analytical Modules")
p_cols = st.columns(3)
with p_cols[0]:
    st.markdown("1. **Overview**: Executive European snapshot\n2. **Country Comparison**: Cross-country metric matrix\n3. **Interest Rates**: Mortgage, corporate, and deposit rates\n4. **Loans & Credit**: Outstanding loans & growth")
with p_cols[1]:
    st.markdown("5. **Deposits**: Household & corporate deposits\n6. **Loans vs Deposits**: Loan-to-Deposit Ratios (LDR)\n7. **Banking Profitability**: ROE & ROA metrics\n8. **Banking Risk**: NPL ratios & capital adequacy")
with p_cols[2]:
    st.markdown("9. **Lending Conditions**: Bank Lending Survey (BLS)\n10. **Monetary Policy**: ECB policy rate transmission\n11. **Country Analysis**: Single country deep-dive\n12. **Data Quality & Sources**: Audit logs\n13. **Executive Reports**: Data insights & bar analysis")
