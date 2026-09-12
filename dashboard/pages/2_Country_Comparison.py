import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sql.analytics import AnalyticsEngine
from dashboard.components.filters import render_sidebar_filters

st.set_page_config(page_title="Country Comparison | European Banking Analytics", layout="wide")
st.title("📊 Cross-Country Comparison Matrix")
st.markdown("Compare European banking indicators, interest rates, inflation, and lending conditions across multiple economies.")

selected_countries, start_year, end_year = render_sidebar_filters()

analytics = AnalyticsEngine()
df_snapshot = analytics.get_latest_country_snapshot(selected_countries)

if not df_snapshot.empty:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Interactive Comparative Matrix")
        st.dataframe(df_snapshot, use_container_width=True)

    with col2:
        st.markdown("### Mortgage Rate vs Inflation Rate")
        df_clean = df_snapshot.dropna(subset=["inflation_rate", "mortgage_rate"])
        if not df_clean.empty:
            st.scatter_chart(df_clean, x="inflation_rate", y="mortgage_rate", color="region")
        else:
            st.info("No matching inflation & rate pairs for selected countries.")
else:
    st.info("Please select countries from the sidebar to generate comparative analysis.")
