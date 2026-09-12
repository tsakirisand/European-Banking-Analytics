import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sql.analytics import AnalyticsEngine
from dashboard.components.filters import render_sidebar_filters

st.set_page_config(page_title="Banking Profitability | European Banking Analytics", layout="wide")
st.title("📈 Banking Sector Profitability (ROE & ROA)")
st.markdown("Consolidated Banking Data (CBD2) analyzing Return on Equity (ROE) and Return on Assets (ROA) across European banking systems.")

selected_countries, start_year, end_year = render_sidebar_filters()

st.info("ℹ️ **Data Transparency**: Consolidated Banking Data (CBD2) indicators track structural profitability metrics across European commercial banking sectors.")

analytics = AnalyticsEngine()
df_prof = analytics.get_banking_profitability(selected_countries, start_year, end_year)

if not df_prof.empty:
    tab1, tab2, tab3 = st.tabs(["📊 Return on Equity (ROE %)", "📈 Return on Assets (ROA %)", "📋 Summary Matrix"])
    
    with tab1:
        st.markdown("### Return on Equity (ROE %) Trends")
        df_roe = df_prof[df_prof["indicator_code"] == "CBD2_ROE"]
        if not df_roe.empty:
            pivoted_roe = df_roe.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
            st.line_chart(pivoted_roe)
            
            st.markdown("#### Latest ROE Values per Country (%)")
            latest_roe = df_roe.sort_values("period_date").groupby("country_code").last().reset_index()
            st.bar_chart(latest_roe.set_index("country_name")["obs_value"])
        else:
            st.info("No ROE data available for selected filter criteria.")

    with tab2:
        st.markdown("### Return on Assets (ROA %) Trends")
        df_roa = df_prof[df_prof["indicator_code"] == "CBD2_ROA"]
        if not df_roa.empty:
            pivoted_roa = df_roa.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
            st.line_chart(pivoted_roa)
            
            st.markdown("#### Latest ROA Values per Country (%)")
            latest_roa = df_roa.sort_values("period_date").groupby("country_code").last().reset_index()
            st.bar_chart(latest_roa.set_index("country_name")["obs_value"])
        else:
            st.info("No ROA data available for selected filter criteria.")

    with tab3:
        st.markdown("### European Banking Profitability Summary Table")
        pivoted_all = df_prof.pivot_table(index=["country_name", "indicator_name"], columns="date_key", values="obs_value")
        st.dataframe(pivoted_all, use_container_width=True)

        st.download_button(
            label="📥 Download Profitability Dataset",
            data=df_prof.to_csv(index=False),
            file_name="european_banking_profitability.csv",
            mime="text/csv"
        )
else:
    st.info("Select countries and time horizon from the sidebar to display profitability metrics.")
