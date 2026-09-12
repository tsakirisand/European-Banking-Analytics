import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sql.analytics import AnalyticsEngine
from dashboard.components.filters import render_sidebar_filters

st.set_page_config(page_title="Country Comparison | European Banking Analytics", layout="wide")
st.title("📊 Cross-Country Comparison Matrix & Bar Analytics")
st.markdown("Compare European banking indicators, interest rates, inflation, and lending conditions across multiple economies.")

selected_countries, start_year, end_year = render_sidebar_filters()

analytics = AnalyticsEngine()
df_snapshot = analytics.get_latest_country_snapshot(selected_countries)

if not df_snapshot.empty:
    tab1, tab2 = st.tabs(["📋 Comparative Matrix & Scatter", "📊 Bar Chart Comparisons"])
    
    with tab1:
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

    with tab2:
        st.markdown("### Cross-Country Metric Bar Charts")
        c_b1, c_b2 = st.columns(2)
        
        with c_b1:
            st.markdown("#### Commercial Mortgage Rates by Country (%)")
            st.bar_chart(df_snapshot.set_index("country_name")["mortgage_rate"])

        with c_b2:
            st.markdown("#### Corporate Lending Rates by Country (%)")
            st.bar_chart(df_snapshot.set_index("country_name")["corp_lending_rate"])

        c_b3, c_b4 = st.columns(2)

        with c_b3:
            st.markdown("#### Deposit Rates by Country (%)")
            st.bar_chart(df_snapshot.set_index("country_name")["deposit_rate"])

        with c_b4:
            st.markdown("#### GDP Per Capita (€ / inhabitant)")
            st.bar_chart(df_snapshot.set_index("country_name")["gdp_per_capita"])

        st.download_button(
            label="📥 Download Comparison Matrix (CSV)",
            data=df_snapshot.to_csv(index=False),
            file_name="cross_country_comparison_matrix.csv",
            mime="text/csv"
        )
else:
    st.info("Please select countries from the sidebar to generate comparative analysis.")
