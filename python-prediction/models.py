from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    feeder11_id: int = Field(..., description="ID Feeders11 zapisa")
    hours: int       = Field(168, ge=1, le=8760, description="Prozor analize u satima (default: 7 dana)")


class NetworkScanRequest(BaseModel):
    hours: int         = Field(168, ge=1, le=8760)
    use_forecast: bool = Field(False, description="Zadržano zbog kompatibilnosti, ali se ne koristi")
    top_n: int         = Field(20, ge=1, le=200, description="Koliko najkritičnijih da vrati")

class ForecastRequest(BaseModel):
    feeder11_id: int  = Field(..., description="ID Feeders11 zapisa")
    hours: int        = Field(168, ge=1, le=8760, description="Koliko istorijskih sati koristimo za trening")
    horizon_hours: int = Field(24, ge=1, le=168,  description="Koliko sati unapred predvidjamo")
    
class AnomalyPoint(BaseModel):
    meter_id: int
    timestamp: str
    value: float
    zscore: float
    anomaly_score: float


class GapEvent(BaseModel):
    meter_id: int
    start: str
    end: str
    duration_h: float

class ForecastPoint(BaseModel):
    timestamp: str
    predicted_value: float
    lower_bound: float
    upper_bound: float
    is_high_load: bool
 
 
class HighLoadWindow(BaseModel):
    start: str
    end: str


class AnalyzeResponse(BaseModel):
    feeder11_id: int
    from_cache: bool
    status: Literal["OK", "WARNING", "CRITICAL", "NO_DATA"]
    risk_score: float
    total_readings: int
    total_outages: int
    anomaly_count: int
    anomaly_rate: float
    avg_load: float
    max_load: float
    max_gap_hours: float
    anomalies: list[AnomalyPoint] = []
    gaps: list[GapEvent] = []

    forecast_points: list = []
    predicted_peak_load: float = 0.0
    high_risk_windows: list = []
    method_used: str = "none"
    horizon_hours: int = 0


class FeederSummary(BaseModel):
    feeder11_id: int
    name: str
    status: Literal["OK", "WARNING", "CRITICAL", "NO_DATA"]
    risk_score: float
    anomaly_rate: float
    max_gap_hours: float
    total_readings: int


class NetworkScanResponse(BaseModel):
    scanned: int
    critical_count: int
    warning_count: int
    ok_count: int
    feeders: list[FeederSummary]

class ForecastResponse(BaseModel):
    feeder11_id: int
    method_used: str
    horizon_hours: int
    predicted_peak: float
    high_load_windows: list[HighLoadWindow] = []
    forecast_points: list[ForecastPoint]   = []

