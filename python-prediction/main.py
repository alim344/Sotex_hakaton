import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from contextlib import asynccontextmanager
from prediction import forecast_feeder
from database import engine, get_feeder_readings, get_all_feeders
from analysis import analyze_feeder, detect_gaps_only, _risk_score
from models import (
    AnalyzeRequest, AnalyzeResponse,
    NetworkScanRequest, NetworkScanResponse,
    FeederSummary, AnomalyPoint, GapEvent, ForecastResponse, ForecastRequest, ForecastPoint, HighLoadWindow
)
from update_db import run_database_cleanup
from overload import get_overload_history_from_db

import logging
log = logging.getLogger("sotex")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\nServer se pokreće — čišćenje baze u toku...")
    try:
        run_database_cleanup()
        print("Čišćenje završeno. Server je spreman.\n")
    except Exception as e:
        print(f"UPOZORENJE: Čišćenje baze nije uspelo: {e}")
        print("Server nastavlja sa radom bez čišćenja.\n")
    yield

app = FastAPI(
    title="Sotex Outage & Anomaly Detection API",
    version="3.1.0",
    description="Detekcija prekida merenja (gap-ova), anomalija potrošnje i istorije preopterećenja.",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_analyze_cache = {}
_forecast_cache = {}


def _build_response(feeder11_id: int, analysis: dict, from_cache: bool) -> AnalyzeResponse:
    return AnalyzeResponse(
        feeder11_id=feeder11_id,
        from_cache=from_cache,
        status=analysis["status"],
        risk_score=analysis["risk_score"],
        total_readings=analysis["total_readings"],
        total_outages=analysis["total_outages"],
        anomaly_count=analysis["anomaly_count"],
        anomaly_rate=analysis["anomaly_rate"],
        avg_load=analysis["avg_load"],
        max_load=analysis["max_load"],
        max_gap_hours=analysis["max_gap_hours"],
        anomalies=[AnomalyPoint(**a) for a in analysis.get("anomalies", [])],
        gaps=[GapEvent(**g) for g in analysis.get("gaps", [])],
        forecast_points=[],
        predicted_peak_load=0.0,
        high_risk_windows=[],
        method_used="none",
        horizon_hours=0,
    )

@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    key = (req.feeder11_id, req.hours)
    if key in _analyze_cache:
        log.info("Cache hit (analyze): feeder=%d", req.feeder11_id)
        return _build_response(req.feeder11_id, _analyze_cache[key], True)

    df = get_feeder_readings(req.feeder11_id, req.hours)
    if df.empty:
        raise HTTPException(404, f"Nema podataka za Feeder11 ID={req.feeder11_id} u poslednjih {req.hours} sati.")

    analysis = analyze_feeder(df)
    _analyze_cache[key] = analysis
    return _build_response(req.feeder11_id, analysis, False)

@app.post("/network/scan", response_model=NetworkScanResponse)
def network_scan(req: NetworkScanRequest):
    feeders_df = get_all_feeders()
    if feeders_df.empty:
        raise HTTPException(404, "Nema Feeders11 zapisa u bazi.")

    results = []
    for _, row in feeders_df.iterrows():
        fid = int(row["Id"])
        name = str(row["Name"])
        try:
            df = get_feeder_readings(fid, req.hours)
            analysis = analyze_feeder(df)
            results.append(FeederSummary(
                feeder11_id=fid,
                name=name,
                status=analysis["status"],
                risk_score=analysis["risk_score"],
                anomaly_rate=analysis["anomaly_rate"],
                max_gap_hours=analysis["max_gap_hours"],
                total_readings=analysis["total_readings"],
            ))
        except Exception as e:
            log.warning("Greška za feeder %d (%s): %s", fid, name, e)
            results.append(FeederSummary(
                feeder11_id=fid, name=name, status="NO_DATA",
                risk_score=0.0, anomaly_rate=0.0, max_gap_hours=0.0, total_readings=0
            ))

    results.sort(key=lambda r: r.risk_score, reverse=True)
    return NetworkScanResponse(
        scanned=len(results),
        critical_count=sum(1 for r in results if r.status == "CRITICAL"),
        warning_count=sum(1 for r in results if r.status == "WARNING"),
        ok_count=sum(1 for r in results if r.status == "OK"),
        feeders=results[:req.top_n],
    )

@app.post("/forecast", response_model=ForecastResponse)
def forecast(req: ForecastRequest):
    """
    Predikcija potrošnje za Feeder11.
 
    - Koristi SARIMA(1,1,1)(1,0,1)[48] ako ima dovoljno podataka
    - Fallback na naive (prosek istog sata/dana u nedelji)
    - Predviđa consumption_per_hour (kWh/h) — bez normalizacije na NameplateRating
    - Prag za 'visoku potrošnju' = 90. percentil istorijskih vrednosti
    """
    key = (req.feeder11_id, req.hours, req.horizon_hours)
    if key in _forecast_cache:
        cached = _forecast_cache[key]
        return ForecastResponse(
            feeder11_id=req.feeder11_id,
            **cached,
        )
 
    df = get_feeder_readings(req.feeder11_id, req.hours)
    if df.empty:
        raise HTTPException(404, f"Nema podataka za Feeder11 ID={req.feeder11_id}.")
 
    result = forecast_feeder(df, req.horizon_hours)
 
    if result["method_used"] == "none":
        raise HTTPException(422, "Nedovoljno podataka za predikciju (minimum 48 ocitavanja).")
 
    _forecast_cache[key] = result
 
    return ForecastResponse(
        feeder11_id=req.feeder11_id,
        method_used=result["method_used"],
        horizon_hours=result["horizon_hours"],
        predicted_peak=result["predicted_peak"],
        high_load_windows=[HighLoadWindow(**w) for w in result["high_load_windows"]],
        forecast_points=[ForecastPoint(**p) for p in result["forecast_points"]],
    )

@app.get("/feeders")
def list_feeders():
    df = get_all_feeders()
    return [] if df.empty else df.to_dict(orient="records")

@app.get("/gaps")
def get_gaps(feeder11_id: int, hours: int = 168, gap_threshold_minutes: int = 95):
    df = get_feeder_readings(feeder11_id, hours)
    if df.empty:
        raise HTTPException(404, "Nema podataka za dati feeder.")
    gaps = detect_gaps_only(df, gap_threshold_minutes)
    return {
        "feeder11_id": feeder11_id,
        "total_gaps": len(gaps),
        "max_gap_hours": max((g["duration_h"] for g in gaps), default=0.0),
        "gaps": gaps
    }

@app.get("/history/{feeder_id}")
def get_feeder_history(feeder_id: int):
    try:
        df = get_overload_history_from_db(engine, feeder_id)
        if df.empty:
            return []
        records = df.to_dict(orient="records")
        for record in records:
            if 'timestamp' in record and record['timestamp']:
                if isinstance(record['timestamp'], str):
                    record['timestamp'] = record['timestamp'].replace(" ", "T")
                else:
                    record['timestamp'] = record['timestamp'].isoformat()
        return records
    except Exception as e:
        log.error(f"History error: {e}")
        return []

@app.delete("/cache")
def clear_cache():
    count_a = len(_analyze_cache)
    _analyze_cache.clear()
    return {"message": f"Obrisano {count_a} keširanih rezultata ({count_a} analyze."}

@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        raise HTTPException(503, f"DB nedostupna: {e}")