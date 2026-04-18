import pandas as pd
import numpy as np

# def clean_and_augment_data(df_readings, df_feeders):

#     df_feeders['NameplateRating'] = df_feeders['NameplateRating'].replace(0, np.nan)

#     df_feeders['NameplateRating'] = pd.to_numeric(df_feeders['NameplateRating'], errors='coerce')
#     df_feeders['SsId'] = pd.to_numeric(df_feeders['SsId'], errors='coerce')
#     df_feeders['TsId'] = pd.to_numeric(df_feeders['TsId'], errors='coerce')

#     df_feeders['NameplateRating'] = df_feeders['NameplateRating'].replace(0, np.nan)

#     df_feeders['TemporaryKey'] = df_feeders.apply(make_key, axis=1)

#     df_feeders['NameplateRating'] = df_feeders['NameplateRating'].fillna(
#         df_feeders.groupby('TemporaryKey')['NameplateRating'].transform('mean')
#     )

#     preostalo_nan = df_feeders['NameplateRating'].isnull().sum()
#     if preostalo_nan > 0:
#         df_feeders['NameplateRating'] = df_feeders['NameplateRating'].fillna(df_feeders['NameplateRating'].mean())

#     df_readings['timestamp'] = pd.to_datetime(df_readings['timestamp'])

#     return df_readings, df_feeders


def analyze_data(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "total_outages": 0, "total_readings": 0, "avg_load": 0.0,
            "max_load": 0.0, "max_gap_hours": 0.0, "risk_score": 0.0,
            "status": "UNKNOWN", "anomalies_found": 0, "prediction": "Nema podataka"
        }

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(["meter_id", "timestamp"])
    df = df.drop_duplicates(subset=['meter_id', 'timestamp'])
    
    df["gap"] = df.groupby("meter_id")["timestamp"].diff().dt.total_seconds() / 60
    
    major_outages = df[df["gap"] > 65]
    total_major_outages = len(major_outages)
    
    max_gap_hrs = round(df["gap"].max() / 60, 2) if not df["gap"].empty else 0.0

    df['moving_avg'] = df['value'].rolling(window=4).mean()
    df['std_dev'] = df['value'].rolling(window=4).std()
    
    anomalies = df[df['value'] > (df['moving_avg'] + 2 * df['std_dev'])]
    anomalies_count = len(anomalies)

    avg_load = df["value"].mean()
    max_load = df["value"].max()
    total_readings = len(df)

    base_risk = (total_major_outages * 0.2) + (anomalies_count * 0.05)
    
    if max_gap_hrs > 5:
        base_risk += 0.3
        
    risk_score = round(min(base_risk, 1.0), 2)

    if risk_score > 0.7:
        status = "CRITICAL"
        prediction_msg = "VISOK RIZIK: Moguć trajni kvar na mreži!"
    elif risk_score > 0.3:
        status = "WARNING"
        prediction_msg = "Srednji rizik: Detektovane nestabilnosti u radu."
    else:
        status = "OK"
        prediction_msg = "Sistem je stabilan. Nema predviđenih kvarova."

    return {
        "total_outages": int(total_major_outages),
        "total_readings": int(total_readings),
        "avg_load": round(float(avg_load), 2),
        "max_load": round(float(max_load), 2),
        "max_gap_hours": float(max_gap_hrs),
        "risk_score": float(risk_score),
        "status": status,
        "anomalies_found": int(anomalies_count),
        "prediction": prediction_msg
    }