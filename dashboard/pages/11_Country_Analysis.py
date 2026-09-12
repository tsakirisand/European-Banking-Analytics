import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sql.analytics import AnalyticsEngine
from config.countries import EUROPEAN_COUNTRIES

st.set_page_config(page_title="Country Analysis | European Banking Analytics", layout="wide")
st.title("🔍 Single Country Financial Profile")
st.markdown("Deep-dive financial, interest rate, credit, and macroeconomic profile for any selected European country.")

selected_code = st.selectbox("Select Country Profile", [c for c in EUROPEAN_COUNTRIES.keys() if c != "U2"], index=0)
info = EUROPEAN_COUNTRIES[selected_code]

st.markdown(f"## {info['name']} ({selected_code})")
col_a, col_b, col_c = st.columns(3)
with col_a:
    st.metric("Region", info['region'])
with col_b:
    st.metric("Euro Area Member", "Yes" if info['is_ea'] else "No")
with col_c:
    st.metric("EU Member", "Yes" if info['is_eu'] else "No")

st.markdown("---")

analytics = AnalyticsEngine()
profile = analytics.get_country_full_profile(selected_code)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Interest Rates",
    "💳 Loans & Credit",
    "🌐 Macroeconomics",
    "📑 Bank Lending Survey",
    "🛡️ Banking Sector Performance"
])

with tab1:
    df_rates = profile["rates"]
    if not df_rates.empty:
        st.markdown("### Commercial Interest Rate History")
        pivoted_r = df_rates.pivot_table(index="period_date", columns="indicator_name", values="obs_value", aggfunc="first")
        st.line_chart(pivoted_r)
        st.dataframe(df_rates.tail(15), use_container_width=True)
    else:
        st.info(f"No interest rate history recorded for {info['name']}.")

with tab2:
    df_loans = profile["loans"]
    if not df_loans.empty:
        st.markdown("### Outstanding Loan & Credit Stock (€ Million)")
        pivoted_l = df_loans.pivot_table(index="period_date", columns="indicator_name", values="obs_value", aggfunc="first")
        st.line_chart(pivoted_l)
        st.dataframe(df_loans.tail(15), use_container_width=True)
    else:
        st.info(f"No loans & credit stock history recorded for {info['name']}.")

with tab3:
    df_macro = profile["macro"]
    if not df_macro.empty:
        st.markdown("### Macroeconomic Indicators (HICP, GDP, Population)")
        
        col_m1, col_m2 = st.columns(2)
        df_hicp = df_macro[df_macro["indicator_code"] == "EUROSTAT_HICP"]
        with col_m1:
            if not df_hicp.empty:
                st.markdown("#### HICP Inflation Rate (%)")
                st.line_chart(df_hicp.set_index("period_date")["obs_value"])
        
        df_gdp_pc = df_macro[df_macro["indicator_code"] == "EUROSTAT_GDP_PC"]
        with col_m2:
            if not df_gdp_pc.empty:
                st.markdown("#### GDP Per Capita (€ / inhabitant)")
                st.line_chart(df_gdp_pc.set_index("period_date")["obs_value"])

        st.dataframe(df_macro.tail(15), use_container_width=True)
    else:
        st.info(f"No macroeconomic indicators recorded for {info['name']}.")

with tab4:
    df_bls = profile["bls"]
    if not df_bls.empty:
        st.markdown("### Bank Lending Survey (Net % Net Tightening / Easing)")
        st.line_chart(df_bls.set_index("period_date")["obs_value"])
        st.dataframe(df_bls.tail(15), use_container_width=True)
    else:
        st.info(f"No Bank Lending Survey data recorded for {info['name']}.")

with tab5:
    df_bank = profile.get("banking", pd.DataFrame())
    if not df_bank.empty:
        st.markdown("### Consolidated Banking Sector Indicators (ROE, ROA, NPL, CET1)")
        pivoted_b = df_bank.pivot_table(index="period_date", columns="indicator_name", values="obs_value", aggfunc="first")
        st.line_chart(pivoted_b)
        st.dataframe(df_bank, use_container_width=True)
    else:
        st.info(f"No banking sector indicators recorded for {info['name']}.")
