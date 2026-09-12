import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sql.analytics import AnalyticsEngine
from dashboard.components.filters import render_sidebar_filters

st.set_page_config(page_title="Lending Conditions | European Banking Analytics", layout="wide")
st.title("📑 Bank Lending Survey (BLS)")
st.markdown("Track net percentage changes in credit standards (tightening/easing) and loan demand across European banks.")

st.info("💡 **Interpretation**: Positive net percentages indicate a net tightening of credit standards by commercial banks, while negative values indicate net easing.")

selected_countries, start_year, end_year = render_sidebar_filters()

analytics = AnalyticsEngine()
df_bls = analytics.get_bls_survey(selected_countries, start_year, end_year)

if not df_bls.empty:
    st.markdown("### Enterprise Credit Standards Net Percentage (Tightening / Easing)")
    pivoted = df_bls.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
    st.line_chart(pivoted)
    st.dataframe(pivoted.tail(16), use_container_width=True)
else:
    st.info("Select countries from sidebar to view Bank Lending Survey indices.")
