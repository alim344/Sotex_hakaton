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

def get_feeder_readings(feeder11_id: int, hours: int = 168) -> pd.DataFrame:
   
    q = text("""
        DECLARE @cutoff DATETIME =
            DATEADD(hour, -:hours, (SELECT MAX(Ts) FROM dbo.MeterReadTfes));
 
        SELECT
            m.Mid                AS meter_id,
            m.Val                AS value,
            m.Ts                 AS timestamp,
            me.MultiplierFactor  AS multiplier,
            f.NameplateRating    AS nameplate_rating
        FROM  dbo.MeterReadTfes         m
        JOIN  dbo.Meters                me ON me.Id      = m.Mid
        JOIN  dbo.DistributionSubstation ds ON ds.MeterId = me.Id
        JOIN  dbo.Feeders11             f  ON f.Id       = ds.Feeder11Id
        WHERE ds.Feeder11Id = :fid
          AND m.Ts >= @cutoff
        ORDER BY m.Mid, m.Ts
    """)
    with engine.connect() as conn:
        df = pd.read_sql(q, conn, params={"fid": feeder11_id, "hours": hours})
 
    if df.empty:
        return df
 
    df["multiplier"] = df["multiplier"].fillna(1.0)
    df["value"] = df["value"] * df["multiplier"]
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
 
 
def get_all_feeders() -> pd.DataFrame:
    q = text("SELECT Id, Name, NameplateRating FROM dbo.Feeders11")
    with engine.connect() as conn:
        return pd.read_sql(q, conn)
 
 
def get_secondary_channels(feeder11_id: int, hours: int = 168) -> pd.DataFrame:
    q = text("""
        DECLARE @cutoff DATETIME =
            DATEADD(hour, -:hours, (SELECT MAX(Ts) FROM dbo.MeterReads));
 
        SELECT
            mr.Mid   AS meter_id,
            mr.Val   AS value,
            mr.Ts    AS timestamp,
            ch.Name  AS channel_name,
            ch.Unit  AS unit
        FROM  dbo.MeterReads             mr
        JOIN  dbo.Channels               ch ON ch.Id      = mr.Cid
        JOIN  dbo.Meters                 me ON me.Id      = mr.Mid
        JOIN  dbo.DistributionSubstation ds ON ds.MeterId = me.Id
        WHERE ds.Feeder11Id = :fid
          AND mr.Ts >= @cutoff
        ORDER BY mr.Mid, mr.Ts
    """)
    with engine.connect() as conn:
        df = pd.read_sql(q, conn, params={"fid": feeder11_id, "hours": hours})
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df