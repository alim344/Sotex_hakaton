from pydantic import BaseModel

class PredictRequest(BaseModel):
    feeder11_id: int
    hours: int = 24

class PredictResponse(BaseModel):
    feeder11_id: int
    status: str
    risk_score: float
    total_outages: int
    total_readings: int
    avg_load: float
    max_load: float
    max_gap_hours: float
    from_cache: bool