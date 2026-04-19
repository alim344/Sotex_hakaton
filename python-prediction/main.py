from __future__ import annotations

import logging
from functools import lru_cache

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import engine, get_feeder_readings, get_all_feeders
from analysis import analyze_feeder, detect_gaps_only
from models import (
    AnalyzeRequest, AnalyzeResponse,
    NetworkScanRequest, NetworkScanResponse,
    FeederSummary, AnomalyPoint, GapEvent,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("sotex")

app = FastAPI(
    title="Sotex Outage & Anomaly Detection API",
    version="3.0.0",
    description="Detekcija prekida merenja (gap-ova) i anomalija potrošnje (bez upotrebe nameplate ratinga).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
_cache: dict[tuple, dict] = {}

def _cache_key(req: AnalyzeRequest) -> tuple:
    return (req.feeder11_id, req.hours)


def _build_response(
    feeder11_id: int,
    analysis: dict,
    from_cache: bool,
) -> AnalyzeResponse:
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

@app.post("/analyze", response_model=AnalyzeResponse, summary="Detaljna analiza feedera (anomalije + gapovi)")
def analyze(req: AnalyzeRequest):
    key = (req.feeder11_id, req.hours)
    if key in _cache:
        log.info("Cache hit: feeder=%d", req.feeder11_id)
        cached = _cache[key]
        return _build_response(req.feeder11_id, cached["analysis"], True)

    log.info("Analiza feedera %d (%d h)...", req.feeder11_id, req.hours)
    df = get_feeder_readings(req.feeder11_id, req.hours)

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Nema podataka za Feeder11 ID={req.feeder11_id} u poslednjih {req.hours} sati.",
        )

    analysis = analyze_feeder(df)
    _cache[key] = {"analysis": analysis}
    log.info(
        "Feeder %d → status=%s risk=%.3f anomalies=%d outages=%d",
        req.feeder11_id, analysis["status"], analysis["risk_score"],
        analysis["anomaly_count"], analysis["total_outages"],
    )

    return _build_response(req.feeder11_id, analysis, False)


@app.post("/network/scan", response_model=NetworkScanResponse, summary="Skeniranje cele mreže")
def network_scan(req: NetworkScanRequest):
    feeders_df = get_all_feeders()
    if feeders_df.empty:
        raise HTTPException(status_code=404, detail="Nema Feeders11 zapisa u bazi.")

    results: list[FeederSummary] = []

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
                feeder11_id=fid,
                name=name,
                status="NO_DATA",
                risk_score=0.0,
                anomaly_rate=0.0,
                max_gap_hours=0.0,
                total_readings=0,
            ))

    results.sort(key=lambda r: r.risk_score, reverse=True)

    return NetworkScanResponse(
        scanned=len(results),
        critical_count=sum(1 for r in results if r.status == "CRITICAL"),
        warning_count=sum(1 for r in results if r.status == "WARNING"),
        ok_count=sum(1 for r in results if r.status == "OK"),
        feeders=results[: req.top_n],
    )


@app.get("/feeders", summary="Lista svih Feeders11")
def list_feeders():
    df = get_all_feeders()
    if df.empty:
        return []
    return df.to_dict(orient="records")


@app.delete("/cache", summary="Briši keš")
def clear_cache():
    count = len(_cache)
    _cache.clear()
    return {"message": f"Obrisano {count} keširanih rezultata."}


@app.get("/health", summary="Health check")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB nedostupna: {e}")


@app.get("/gaps", summary="Samo prekidi merenja (gap-ovi)")
def get_gaps(feeder11_id: int, hours: int = 168, gap_threshold_minutes: int = 95):
    df = get_feeder_readings(feeder11_id, hours)
    if df.empty:
        raise HTTPException(status_code=404, detail="Nema podataka za dati feeder.")
    gaps = detect_gaps_only(df, gap_threshold_minutes)
    return {
        "feeder11_id": feeder11_id,
        "total_gaps": len(gaps),
        "max_gap_hours": max((g["duration_h"] for g in gaps), default=0.0),
        "gaps": gaps
    }