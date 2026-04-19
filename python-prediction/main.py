import pandas as pd
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from database import engine
from analysis import analyze_data
from models import PredictRequest, PredictResponse
from contextlib import asynccontextmanager
from update_db import run_database_cleanup
from overload import get_overload_history_from_db

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

app = FastAPI(title="Sotex Outage Prediction")
#app = FastAPI(title="Sotex Outage Prediction", lifespan=lifespan)

_cache = {}

def get_readings_from_db(feeder_id: int, hours: int) -> pd.DataFrame:
    query = text("""
        DECLARE @MaxDate DATETIME = (SELECT MAX(Ts) FROM dbo.MeterReadTfes);
 
        SELECT
            m.Mid AS meter_id,
            m.Val AS value,
            m.Ts  AS timestamp
        FROM dbo.MeterReadTfes m
        JOIN dbo.Meters me              ON m.Mid      = me.Id
        JOIN dbo.DistributionSubstation ds ON ds.MeterId = me.Id
        WHERE ds.Feeder11Id = :feeder_id
        AND   m.Ts >= DATEADD(hour, -:hours, @MaxDate)
        ORDER BY m.Mid, m.Ts
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={"feeder_id": feeder_id, "hours": hours})

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    """
    Prima feeder11_id i broj sati unazad.
    Vraća procenu rizika od kvara.
 
    Primer:
        POST /predict
        { "feeder11_id": 1, "hours": 24 }
    """
    cache_key = (req.feeder11_id, req.hours)
 
    # Vrati iz cache-a ako postoji
    if cache_key in _cache:
        return PredictResponse(feeder11_id=req.feeder11_id, from_cache=True, **_cache[cache_key])
 
    df = get_readings_from_db(req.feeder11_id, req.hours)
 
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Nema podataka za Feeder11 ID={req.feeder11_id} u poslednjih {req.hours} sati."
        )
 
    result = analyze_data(df)
    _cache[cache_key] = result
 
    return PredictResponse(feeder11_id=req.feeder11_id, from_cache=False, **result)
 
 
@app.delete("/cache")
def clear_cache():
    _cache.clear()
    return {"message": "Cache obrisan"}





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
        print(f"Error: {e}")
        return []