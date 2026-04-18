import pyodbc
from sqlalchemy import create_engine, text
import pandas as pd

selected_driver = "{SQL Server}"

CONN_STR = (
    f"DRIVER={selected_driver};"
    "SERVER=localhost,1433;"
    "DATABASE=SotexHackathon;"
    "UID=sa;"
    "PWD=SotexSolutions123!;"
)

def get_raw_conn():
    return pyodbc.connect(CONN_STR, autocommit=True)

engine = create_engine("mssql+pyodbc://", creator=get_raw_conn)

def get_readings_from_db(feeder_id: int, hours: int) -> pd.DataFrame:
    query = text("""
        SELECT 
            m.Mid AS meter_id, 
            m.Val AS value, 
            m.Ts  AS timestamp
        FROM dbo.MeterReadTfes m
        JOIN dbo.Meters me ON m.Mid = me.Id
        JOIN dbo.DistributionSubstation ds ON ds.MeterId = me.Id
        WHERE ds.Feeder11Id = :feeder_id
        AND m.Ts >= DATEADD(hour, -:hours, (SELECT MAX(Ts) FROM dbo.MeterReadTfes))
        ORDER BY m.Ts
    """)
    with engine.connect() as conn:
        return pd.read_sql(query, conn, params={"feeder_id": feeder_id, "hours": hours})

def get_feeders_metadata() -> pd.DataFrame:
    query = text("SELECT Id, Name, SsId, TsId, MeterId, NameplateRating FROM dbo.Feeders11")
    with engine.connect() as conn:
        return pd.read_sql(query, conn)