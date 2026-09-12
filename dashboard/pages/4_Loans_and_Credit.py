import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sql.analytics import AnalyticsEngine
from dashboard.components.filters import render_sidebar_filters

st.set_page_config(page_title="Loans & Credit | European Banking Analytics", layout="wide")
st.title("💳 Bank Loans & Credit Growth")
st.markdown("Track outstanding housing loans, consumer credit, corporate loans, and YoY credit growth across European banking sectors.")

selected_countries, start_year, end_year = render_sidebar_filters()

analytics = AnalyticsEngine()
df_loans = analytics.get_loans_and_credit(selected_countries, start_year, end_year)

if not df_loans.empty:
    ind_options = df_loans["indicator_name"].unique()
    selected_ind = st.selectbox("Select Credit Aggregates", ind_options)
    
    df_filtered = df_loans[df_loans["indicator_name"] == selected_ind]
    if not df_filtered.empty:
        pivoted = df_filtered.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
        st.line_chart(pivoted)
        st.dataframe(pivoted.tail(12), use_container_width=True)
    else:
        st.info("No credit data for the selected aggregate.")
else:
    st.info("Balance Sheet Items (BSI) loan data is reported for Euro Area aggregates and major member economies.")
