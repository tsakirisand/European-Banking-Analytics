import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sql.analytics import AnalyticsEngine
from dashboard.components.filters import render_sidebar_filters

st.set_page_config(page_title="Interest Rates | European Banking Analytics", layout="wide")
st.title("📈 European Interest Rate Analytics")
st.markdown("Analyze commercial mortgage rates, corporate lending rates, household deposit rates, and rate spreads across European banking systems.")

selected_countries, start_year, end_year = render_sidebar_filters()

analytics = AnalyticsEngine()
df_rates = analytics.get_interest_rates(selected_countries, start_year, end_year)

if not df_rates.empty:
    ind_options = df_rates["indicator_name"].unique()
    selected_ind = st.selectbox("Select Interest Rate Indicator", ind_options)
    
    df_filtered = df_rates[df_rates["indicator_name"] == selected_ind]
    if not df_filtered.empty:
        tab1, tab2 = st.tabs(["📈 Interest Rate Trends (Line Chart)", "📊 Latest Rate Comparison (Bar Chart)"])
        
        with tab1:
            pivoted = df_filtered.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
            st.line_chart(pivoted)

            st.markdown("### Summary Statistics for Selected Period")
            st.dataframe(pivoted.describe().T, use_container_width=True)

        with tab2:
            st.markdown(f"### Latest {selected_ind} per Country (%)")
            latest_r = df_filtered.sort_values("period_date").groupby("country_name").last().reset_index()
            st.bar_chart(latest_r.set_index("country_name")["obs_value"])
            st.dataframe(latest_r[["country_code", "country_name", "period_date", "obs_value", "unit"]], use_container_width=True)
    else:
        st.info("No observations available for the selected filter.")
else:
    st.info("No interest rate data found for selected criteria.")
