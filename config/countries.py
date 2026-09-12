"""
European Country Dimension Configuration
Contains official UN/Eurostat country classifications, Euro Area membership dates, and regional groupings.
"""

from typing import Dict, Any, List

EUROPEAN_COUNTRIES: Dict[str, Dict[str, Any]] = {
    "DE": {"name": "Germany", "region": "Western Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 1999},
    "FR": {"name": "France", "region": "Western Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 1999},
    "IT": {"name": "Italy", "region": "Southern Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 1999},
    "ES": {"name": "Spain", "region": "Southern Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 1999},
    "NL": {"name": "Netherlands", "region": "Western Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 1999},
    "BE": {"name": "Belgium", "region": "Western Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 1999},
    "AT": {"name": "Austria", "region": "Western Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 1999},
    "PT": {"name": "Portugal", "region": "Southern Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 1999},
    "IE": {"name": "Ireland", "region": "Western Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 1999},
    "FI": {"name": "Finland", "region": "Northern Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 1999},
    "GR": {"name": "Greece", "region": "Southern Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 2001},
    "CY": {"name": "Cyprus", "region": "Southern Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 2008},
    "MT": {"name": "Malta", "region": "Southern Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 2008},
    "SK": {"name": "Slovakia", "region": "Eastern Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 2009},
    "SI": {"name": "Slovenia", "region": "Eastern Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 2007},
    "EE": {"name": "Estonia", "region": "Northern Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 2011},
    "LV": {"name": "Latvia", "region": "Northern Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 2014},
    "LT": {"name": "Lithuania", "region": "Northern Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 2015},
    "HR": {"name": "Croatia", "region": "Eastern Europe", "is_ea": True, "is_eu": True, "ea_entry_year": 2023},
    "PL": {"name": "Poland", "region": "Eastern Europe", "is_ea": False, "is_eu": True, "ea_entry_year": None},
    "CZ": {"name": "Czechia", "region": "Eastern Europe", "is_ea": False, "is_eu": True, "ea_entry_year": None},
    "HU": {"name": "Hungary", "region": "Eastern Europe", "is_ea": False, "is_eu": True, "ea_entry_year": None},
    "SE": {"name": "Sweden", "region": "Northern Europe", "is_ea": False, "is_eu": True, "ea_entry_year": None},
    "DK": {"name": "Denmark", "region": "Northern Europe", "is_ea": False, "is_eu": True, "ea_entry_year": None},
    "RO": {"name": "Romania", "region": "Eastern Europe", "is_ea": False, "is_eu": True, "ea_entry_year": None},
    "BG": {"name": "Bulgaria", "region": "Eastern Europe", "is_ea": False, "is_eu": True, "ea_entry_year": None},
    "U2": {"name": "Euro Area (changing composition)", "region": "Aggregate", "is_ea": True, "is_eu": True, "ea_entry_year": 1999}
}

REGIONS: Dict[str, List[str]] = {
    "Western Europe": ["DE", "FR", "NL", "BE", "AT", "IE"],
    "Southern Europe": ["IT", "ES", "PT", "GR", "CY", "MT"],
    "Northern Europe": ["FI", "SE", "DK", "EE", "LV", "LT"],
    "Eastern Europe": ["PL", "CZ", "HU", "SK", "SI", "HR", "RO", "BG"]
}

def get_country_info(country_code: str) -> Dict[str, Any]:
    return EUROPEAN_COUNTRIES.get(country_code, {
        "name": country_code,
        "region": "Other",
        "is_ea": False,
        "is_eu": False,
        "ea_entry_year": None
    })
