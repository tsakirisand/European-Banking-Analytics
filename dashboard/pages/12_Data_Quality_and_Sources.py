import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from etl.db_manager import DBManager

st.set_page_config(page_title="Data Quality & Sources | European Banking Analytics", layout="wide")
st.title("🛡️ Data Lineage, Validation Logs & Series Metadata")
st.markdown("Complete data auditability, validation rule execution results (`PASS`, `FAIL`, `WARNING`, `UNVERIFIED`), and official API dataset catalog.")

db = DBManager()

st.markdown("### Registered Datasets Catalog")
with db.get_connection() as conn:
    df_datasets = pd.read_sql_query("SELECT * FROM dim_source", conn)
    st.dataframe(df_datasets, use_container_width=True)

st.markdown("---")
st.markdown("### Registered Indicators Dictionary")
with db.get_connection() as conn:
    df_ind = pd.read_sql_query("SELECT * FROM dim_indicator", conn)
    st.dataframe(df_ind, use_container_width=True)

st.markdown("---")
st.markdown("### Validation Execution Audit Logs")
with db.get_connection() as conn:
    df_logs = pd.read_sql_query("SELECT * FROM validation_logs ORDER BY created_at DESC LIMIT 50", conn)
    st.dataframe(df_logs, use_container_width=True)
