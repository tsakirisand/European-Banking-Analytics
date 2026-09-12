import streamlit as st
from typing import Tuple, List
from config.countries import EUROPEAN_COUNTRIES, REGIONS

def render_sidebar_filters() -> Tuple[List[str], int, int]:
    """
    Renders standardized sidebar controls for all Streamlit analytical pages.
    Returns (selected_countries, start_year, end_year).
    """
    st.sidebar.markdown("## ⚙️ Filters & Controls")
    
    # 1. Region Filter
    selected_region = st.sidebar.selectbox(
        "Select Region", 
        ["All Regions", "Western Europe", "Southern Europe", "Northern Europe", "Eastern Europe"],
        index=0
    )
    
    # Available countries based on region
    country_codes = [c for c in EUROPEAN_COUNTRIES.keys() if c != "U2"]
    if selected_region != "All Regions":
        filtered = REGIONS.get(selected_region, [])
        default_selected = [c for c in filtered if c in country_codes]
    else:
        filtered = country_codes
        default_selected = ["DE", "FR", "IT", "ES", "GR", "NL", "BE", "AT", "PT", "FI"]

    # 2. Country Multiselect
    selected_countries = st.sidebar.multiselect(
        "Select European Countries",
        options=filtered,
        default=default_selected if default_selected else filtered[:5]
    )

    # 3. Date Range Filter
    start_year, end_year = st.sidebar.slider(
        "Time Horizon (Years)",
        min_value=2000,
        max_value=2026,
        value=(2005, 2025)
    )

    return selected_countries, start_year, end_year
