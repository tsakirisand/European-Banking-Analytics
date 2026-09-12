import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sql.analytics import AnalyticsEngine
from dashboard.components.filters import render_sidebar_filters

st.set_page_config(page_title="Deposits | European Banking Analytics", layout="wide")
st.title("🏦 Household & Corporate Deposit Statistics")
st.markdown("Analyze household deposit growth, corporate deposit rates, and total liquidity across European banking systems.")

selected_countries, start_year, end_year = render_sidebar_filters()

analytics = AnalyticsEngine()
df_rates = analytics.get_interest_rates(selected_countries, start_year, end_year)

if not df_rates.empty:
    df_dep = df_rates[df_rates["indicator_code"].isin(["MIR_HH_DEPOSIT", "MIR_CORP_DEPOSIT"])]
    if not df_dep.empty:
        tab1, tab2, tab3 = st.tabs([
            "🏠 Household Deposit Rates (%)",
            "🏢 Corporate Deposit Rates (%)",
            "📊 Comparative Deposit Overview"
        ])

        with tab1:
            st.markdown("### Household Deposit Rates (% per annum)")
            df_hh = df_dep[df_dep["indicator_code"] == "MIR_HH_DEPOSIT"]
            if not df_hh.empty:
                piv_hh = df_hh.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
                st.line_chart(piv_hh)
                
                st.markdown("#### Latest Household Deposit Rates per Country (%)")
                latest_hh = df_hh.sort_values("period_date").groupby("country_code").last().reset_index()
                st.bar_chart(latest_hh.set_index("country_name")["obs_value"])
            else:
                st.info("No household deposit rate data available.")

        with tab2:
            st.markdown("### Corporate Deposit Rates (% per annum)")
            df_corp = df_dep[df_dep["indicator_code"] == "MIR_CORP_DEPOSIT"]
            if not df_corp.empty:
                piv_corp = df_corp.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
                st.line_chart(piv_corp)

                st.markdown("#### Latest Corporate Deposit Rates per Country (%)")
                latest_corp = df_corp.sort_values("period_date").groupby("country_code").last().reset_index()
                st.bar_chart(latest_corp.set_index("country_name")["obs_value"])
            else:
                st.info("No corporate deposit rate data available.")

        with tab3:
            st.markdown("### Deposit Rate Summary Matrix")
            piv_all = df_dep.pivot_table(index=["country_name", "indicator_name"], columns="date_key", values="obs_value")
            st.dataframe(piv_all, use_container_width=True)

            st.download_button(
                label="📥 Download Deposit Rates Dataset",
                data=df_dep.to_csv(index=False),
                file_name="european_deposit_rates.csv",
                mime="text/csv"
            )
    else:
        st.info("No deposit rate data available for selected filter options.")
else:
    st.info("Select countries from sidebar to view deposit rates.")
