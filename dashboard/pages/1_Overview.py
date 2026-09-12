import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sql.analytics import AnalyticsEngine
from dashboard.components.filters import render_sidebar_filters

st.set_page_config(page_title="Overview | European Banking Analytics", layout="wide")
st.title("🇪🇺 European Banking & Financial Overview")
st.markdown("Macro-financial dashboard aggregating banking performance, policy rates, and regional spreads across European economies.")

selected_countries, start_year, end_year = render_sidebar_filters()

analytics = AnalyticsEngine()
df_snapshot = analytics.get_latest_country_snapshot(selected_countries)

st.markdown("### Country Level Snapshot Matrix")
if not df_snapshot.empty:
    st.dataframe(
        df_snapshot.rename(columns={
            "country_code": "Country Code",
            "country_name": "Country Name",
            "region": "Region",
            "mortgage_rate": "Mortgage Rate (%)",
            "corp_lending_rate": "Corporate Rate (%)",
            "deposit_rate": "Deposit Rate (%)",
            "inflation_rate": "HICP Inflation (%)",
            "gdp_per_capita": "GDP Per Capita (€)"
        }),
        use_container_width=True
    )
    
    st.download_button(
        label="📥 Download Overview Dataset",
        data=df_snapshot.to_csv(index=False),
        file_name="european_banking_overview.csv",
        mime="text/csv"
    )
else:
    st.info("Select countries from the sidebar to view metrics.")

st.markdown("---")

tab1, tab2, tab3 = st.tabs([
    "📈 Mortgage Rate Trends",
    "🏢 Corporate Lending Rates",
    "🌐 HICP Inflation Trends"
])

df_rates = analytics.get_interest_rates(selected_countries, start_year, end_year)
df_macro = analytics.get_macro_context(selected_countries, start_year, end_year)

with tab1:
    st.markdown("### Mortgage Interest Rate Trends Over Time (%)")
    if not df_rates.empty:
        df_mort = df_rates[df_rates["indicator_code"] == "MIR_MORTGAGE"]
        if not df_mort.empty:
            pivoted = df_mort.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
            st.line_chart(pivoted)
        else:
            st.info("No mortgage rate data available.")
    else:
        st.info("No interest rate data found.")

with tab2:
    st.markdown("### Corporate Lending Rate Trends Over Time (%)")
    if not df_rates.empty:
        df_corp = df_rates[df_rates["indicator_code"] == "MIR_CORPORATE"]
        if not df_corp.empty:
            pivoted_c = df_corp.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
            st.line_chart(pivoted_c)
        else:
            st.info("No corporate lending rate data available.")
    else:
        st.info("No interest rate data found.")

with tab3:
    st.markdown("### Harmonised Index of Consumer Prices (HICP) Inflation Rate (%)")
    if not df_macro.empty:
        df_hicp = df_macro[df_macro["indicator_code"] == "EUROSTAT_HICP"]
        if not df_hicp.empty:
            pivoted_i = df_hicp.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
            st.line_chart(pivoted_i)
        else:
            st.info("No inflation data available.")
    else:
        st.info("No macroeconomic data found.")
