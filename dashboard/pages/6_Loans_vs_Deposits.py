import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sql.analytics import AnalyticsEngine
from dashboard.components.filters import render_sidebar_filters

st.set_page_config(page_title="Loans vs Deposits | European Banking Analytics", layout="wide")
st.title("⚖️ Loan-to-Deposit Ratio (LDR) & Liquidity Analysis")
st.markdown("Compare structural banking liquidity and loan-to-deposit ratios across European banking sectors.")

st.info("💡 **Methodology**: Loan-to-Deposit Ratio (LDR %) measures banking sector structural liquidity: `LDR (%) = (Total Customer Loans / Total Customer Deposits) * 100`. Ratios above 100% indicate reliance on wholesale market funding.")

selected_countries, start_year, end_year = render_sidebar_filters()

analytics = AnalyticsEngine()
df_loans = analytics.get_loans_and_credit(selected_countries, start_year, end_year)
df_rates = analytics.get_interest_rates(selected_countries, start_year, end_year)

if not df_loans.empty:
    tab1, tab2, tab3 = st.tabs(["💳 Total Loans Stock (€ Million)", "🏦 Deposit Rates & Liquidity", "📊 Credit Aggregates Breakdown"])

    with tab1:
        st.markdown("### Total Outstanding Housing & Corporate Loans (€ Million)")
        df_housing = df_loans[df_loans["indicator_code"] == "BSI_HOUSING_LOANS"]
        if not df_housing.empty:
            pivoted_h = df_housing.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
            st.line_chart(pivoted_h)
            
            st.markdown("#### Latest Housing Loan Stock per Country (€ Million)")
            latest_h = df_housing.sort_values("period_date").groupby("country_code").last().reset_index()
            st.bar_chart(latest_h.set_index("country_name")["obs_value"])
        else:
            st.info("No housing loan stock data available.")

    with tab2:
        st.markdown("### Deposit Interest Rates & Liquidity Spreads")
        if not df_rates.empty:
            df_dep = df_rates[df_rates["indicator_code"].isin(["MIR_HH_DEPOSIT", "MIR_CORP_DEPOSIT"])]
            if not df_dep.empty:
                ind_sel = st.selectbox("Select Deposit Rate Category", df_dep["indicator_name"].unique())
                df_dep_filtered = df_dep[df_dep["indicator_name"] == ind_sel]
                piv_dep = df_dep_filtered.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
                st.line_chart(piv_dep)
            else:
                st.info("No deposit rate metrics found.")
        else:
            st.info("No interest rate dataset available.")

    with tab3:
        st.markdown("### Loans & Credit Aggregates Data Matrix")
        ind_options = df_loans["indicator_name"].unique()
        selected_ind = st.selectbox("Filter by Indicator", ind_options)
        df_f = df_loans[df_loans["indicator_name"] == selected_ind]
        pivoted_f = df_f.pivot_table(index="period_date", columns="country_code", values="obs_value", aggfunc="first")
        st.dataframe(pivoted_f.tail(16), use_container_width=True)

        st.download_button(
            label="📥 Download Loans & Credit Dataset",
            data=df_loans.to_csv(index=False),
            file_name="loans_and_credit_data.csv",
            mime="text/csv"
        )
else:
    st.info("Select countries from the sidebar to view loan-to-deposit and liquidity metrics.")
