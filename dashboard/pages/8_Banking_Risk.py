import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sql.analytics import AnalyticsEngine
from dashboard.components.filters import render_sidebar_filters

st.set_page_config(page_title="Banking Risk | European Banking Analytics", layout="wide")
st.title("🛡️ Banking Risk, Asset Quality & Capital Adequacy")
st.markdown("Monitor Non-Performing Loans (NPL) ratios, Common Equity Tier 1 (CET1) capital ratios, solvency, and liquidity buffers.")

selected_countries, start_year, end_year = render_sidebar_filters()

st.info("ℹ️ **Data Transparency**: Non-Performing Loans (NPL %) ratios and Tier 1 capital ratios represent official EBA and ECB supervisory reporting standards.")

analytics = AnalyticsEngine()
df_risk = analytics.get_banking_risk(selected_countries, start_year, end_year)

if not df_risk.empty:
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚠️ Non-Performing Loans (NPL %)",
        "🏛️ CET1 Capital Adequacy (%)",
        "💧 Liquidity Coverage Ratio (LCR %)",
        "📋 Risk Overview Matrix"
    ])

    with tab1:
        st.markdown("### Non-Performing Loans (NPL Ratio %) Over Time")
        df_npl = df_risk[df_risk["indicator_code"] == "CBD2_NPL"]
        if not df_npl.empty:
            pivoted_npl = df_npl.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
            st.line_chart(pivoted_npl)
            
            st.markdown("#### Latest NPL Ratios per Country (%)")
            latest_npl = df_npl.sort_values("period_date").groupby("country_code").last().reset_index()
            st.bar_chart(latest_npl.set_index("country_name")["obs_value"])
        else:
            st.info("No NPL ratio data available.")

    with tab2:
        st.markdown("### Common Equity Tier 1 (CET1 Ratio %) Trends")
        df_cet1 = df_risk[df_risk["indicator_code"] == "CBD2_CET1"]
        if not df_cet1.empty:
            pivoted_cet1 = df_cet1.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
            st.line_chart(pivoted_cet1)

            st.markdown("#### Latest CET1 Ratios per Country (%)")
            latest_cet1 = df_cet1.sort_values("period_date").groupby("country_code").last().reset_index()
            st.bar_chart(latest_cet1.set_index("country_name")["obs_value"])
        else:
            st.info("No CET1 ratio data available.")

    with tab3:
        st.markdown("### Liquidity Coverage Ratio (LCR %) Buffers")
        df_lcr = df_risk[df_risk["indicator_code"] == "CBD2_LCR"]
        if not df_lcr.empty:
            pivoted_lcr = df_lcr.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
            st.line_chart(pivoted_lcr)

            st.markdown("#### Latest Liquidity Coverage Ratios per Country (%)")
            latest_lcr = df_lcr.sort_values("period_date").groupby("country_code").last().reset_index()
            st.bar_chart(latest_lcr.set_index("country_name")["obs_value"])
        else:
            st.info("No LCR data available.")

    with tab4:
        st.markdown("### European Banking Risk & Capital Matrix")
        latest_all = df_risk.sort_values("period_date").groupby(["country_name", "indicator_name"]).last().reset_index()
        piv_matrix = latest_all.pivot_table(index="country_name", columns="indicator_name", values="obs_value")
        st.dataframe(piv_matrix, use_container_width=True)

        st.download_button(
            label="📥 Download Banking Risk Dataset",
            data=df_risk.to_csv(index=False),
            file_name="european_banking_risk.csv",
            mime="text/csv"
        )
else:
    st.info("Select countries and time horizon from the sidebar to display risk metrics.")
