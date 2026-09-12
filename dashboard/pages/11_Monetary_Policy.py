import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sql.analytics import AnalyticsEngine
from dashboard.components.filters import render_sidebar_filters

st.set_page_config(page_title="Monetary Policy Transmission | European Banking Analytics", layout="wide")
st.title("🎯 ECB Monetary Policy Transmission")
st.markdown("Analyze how ECB policy interest rates (Deposit Facility Rate, Main Refinancing Operations Rate) pass through to commercial mortgage and corporate lending rates across European countries.")

selected_countries, start_year, end_year = render_sidebar_filters()

analytics = AnalyticsEngine()
df_policy = analytics.get_policy_rates()

if not df_policy.empty:
    st.markdown("### Official ECB Key Interest Rates (% per annum)")
    pivoted_p = df_policy.pivot_table(index="period_date", columns="indicator_name", values="obs_value", aggfunc="first")
    st.line_chart(pivoted_p)

st.markdown("---")
st.markdown("### Commercial Mortgage Rate Spread over ECB Deposit Facility Rate (Basis Points)")

df_spreads = analytics.get_rate_spreads(selected_countries)
if not df_spreads.empty:
    pivoted_s = df_spreads.pivot_table(index="period_date", columns="country_code", values="rate_spread_bp", aggfunc="first")
    st.line_chart(pivoted_s)
    st.dataframe(pivoted_s.tail(12), use_container_width=True)
else:
    st.info("Select countries from sidebar to compute rate spreads.")
