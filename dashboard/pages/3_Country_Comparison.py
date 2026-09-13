import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sql.analytics import AnalyticsEngine
from dashboard.components.filters import render_sidebar_filters

st.set_page_config(page_title="Country Comparison | European Banking Analytics", layout="wide")
st.title("📊 Cross-Country Comparison Matrix & Correlation Heatmaps")
st.markdown("Compare European banking indicators, analyze pairwise interest rate co-movements, and explore cross-country financial correlations.")

selected_countries, start_year, end_year = render_sidebar_filters()

analytics = AnalyticsEngine()
df_snapshot = analytics.get_latest_country_snapshot(selected_countries)
df_rates = analytics.get_interest_rates(selected_countries, start_year, end_year)

if not df_snapshot.empty:
    tab1, tab2, tab3 = st.tabs([
        "📋 Comparative Matrix & Scatter",
        "📊 Bar Chart Comparisons",
        "🔥 Cross-Country Correlation Matrix & Heatmap"
    ])
    
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

    with tab3:
        st.markdown("### 🔥 Cross-Country Financial Co-Movement & Correlation Heatmap")
        st.markdown("Analyze pairwise Pearson correlation coefficients ($r$) between European banking systems over the selected time horizon.")
        
        if not df_rates.empty:
            ind_options = df_rates["indicator_name"].unique()
            selected_corr_ind = st.selectbox("Select Indicator for Correlation Analysis", ind_options, index=0)
            
            df_corr_subset = df_rates[df_rates["indicator_name"] == selected_corr_ind]
            if not df_corr_subset.empty:
                piv_corr = df_corr_subset.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
                
                # Drop countries with all NaN values
                piv_corr = piv_corr.dropna(how="all", axis=1)
                
                if piv_corr.shape[1] >= 2:
                    corr_matrix = piv_corr.corr().round(3)
                    
                    # Highlight Metrics
                    corr_values = []
                    cols = corr_matrix.columns
                    for i in range(len(cols)):
                        for j in range(i + 1, len(cols)):
                            val = corr_matrix.iloc[i, j]
                            if not np.isnan(val):
                                corr_values.append((cols[i], cols[j], val))
                    
                    if corr_values:
                        corr_values.sort(key=lambda x: x[2], reverse=True)
                        highest_pair = corr_values[0]
                        lowest_pair = corr_values[-1]
                        avg_corr = np.mean([x[2] for x in corr_values])

                        m1, m2, m3 = st.columns(3)
                        with m1:
                            st.metric("Strongest Co-Movement", f"{highest_pair[0]} - {highest_pair[1]}", f"r = {highest_pair[2]:.3f}")
                        with m2:
                            st.metric("Lowest Co-Movement", f"{lowest_pair[0]} - {lowest_pair[1]}", f"r = {lowest_pair[2]:.3f}")
                        with m3:
                            st.metric("Mean Regional Correlation", f"{avg_corr:.3f}", help="Average pairwise correlation across selected countries")
                    
                    st.markdown(f"#### Pairwise Correlation Heatmap: {selected_corr_ind}")
                    fig = px.imshow(
                        corr_matrix,
                        text_auto=True,
                        color_continuous_scale="Blues",
                        aspect="auto",
                        labels=dict(x="Country Code", y="Country Code", color="Correlation (r)"),
                        title=f"Interest Rate Co-Movement Matrix ({selected_corr_ind})"
                    )
                    fig.update_layout(
                        margin=dict(l=40, r=40, t=50, b=40),
                        font=dict(size=13)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown("#### Full Correlation Matrix Table")
                    st.dataframe(corr_matrix, use_container_width=True)
                else:
                    st.info("Select at least 2 countries with valid data to generate a correlation heatmap.")
            else:
                st.info("No rate observations found for selected indicator.")
        else:
            st.info("No interest rate data found for selected criteria.")

    st.markdown("---")
    st.download_button(
        label="📥 Download Comparison Matrix (CSV)",
        data=df_snapshot.to_csv(index=False),
        file_name="cross_country_comparison_matrix.csv",
        mime="text/csv"
    )
else:
    st.info("Please select countries from the sidebar to generate comparative analysis.")
