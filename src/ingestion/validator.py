from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date, timezone
from typing import Optional, Any
import re

VALID_FREQUENCIES = {"M", "Q", "A", "B", "D"}
VALID_GEOS = {"DE", "FR", "IT", "ES", "GR", "U2", "EU27_2020", "EA19"}

class ObservationSchema(BaseModel):
    dataset_code: str = Field(..., description="ECB or Eurostat dataset code (e.g. MIR, BSI, nama_10_gdp)")
    series_key: str = Field(..., description="Exact series key code")
    geo: str = Field(..., description="ISO country code or regional aggregate")
    frequency: str = Field(..., description="Observation frequency (M, Q, A)")
    period: str = Field(..., description="Raw period identifier (YYYY-MM, YYYY-Qx, YYYY)")
    period_date: Optional[str] = Field(None, description="Normalized ISO date YYYY-MM-DD")
    obs_value: float = Field(..., description="Numeric observation value")
    unit: str = Field(default="", description="Unit of measurement (e.g. %, EUR, Index)")
    retrieval_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, v: str) -> str:
        v_upper = v.upper()
        if v_upper not in VALID_FREQUENCIES:
            raise ValueError(f"Invalid frequency '{v}'. Must be one of {VALID_FREQUENCIES}")
        return v_upper

    @field_validator("obs_value")
    @classmethod
    def validate_obs_value(cls, v: Any) -> float:
        if v is None:
            raise ValueError("Observation value cannot be None")
        try:
            val = float(v)
            return val
        except (ValueError, TypeError):
            raise ValueError(f"Invalid numeric observation value: {v}")

    @field_validator("period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("Period must be a non-empty string")
        return v.strip()

def normalize_period_to_date(period: str, frequency: str) -> Optional[str]:
    """Converts ECB/Eurostat period formats (YYYY, YYYY-MM, YYYY-Qx) to ISO date YYYY-MM-DD."""
    p = period.strip()
    try:
        if re.match(r"^\d{4}$", p):
            return f"{p}-01-01"
        elif re.match(r"^\d{4}-\d{2}$", p):
            return f"{p}-01"
        elif re.match(r"^\d{4}-Q[1-4]$", p):
            year, q = p.split("-Q")
            month = (int(q) - 1) * 3 + 1
            return f"{year}-{month:02d}-01"
        elif re.match(r"^\d{4}Q[1-4]$", p):
            year = p[:4]
            q = p[5]
            month = (int(q) - 1) * 3 + 1
            return f"{year}-{month:02d}-01"
    except Exception:
        pass
    return None
