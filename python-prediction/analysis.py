from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

OUTAGE_GAP_MINUTES = 95
IF_CONTAMINATION   = 0.05


def _to_consumption(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("timestamp").copy()
    df["consumption"] = df["value"].diff()

    df.loc[df["consumption"] < 0, "consumption"] = np.nan
    df.loc[df["consumption"].isna(), "consumption"] = df["consumption"].median()

    df["gap_min"] = df["timestamp"].diff().dt.total_seconds().div(60).fillna(30)
    df["gap_min"] = df["gap_min"].clip(lower=1)
    df["consumption_per_hour"] = df["consumption"] / df["gap_min"] * 60

    return df


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    df = _to_consumption(df)

    c = df["consumption_per_hour"]

    df["roll_mean_2"] = c.rolling(2, min_periods=1).mean()
    df["roll_mean_6"] = c.rolling(6, min_periods=1).mean()
    df["roll_std_2"]  = c.rolling(2, min_periods=1).std().fillna(0)
    df["roll_std_6"]  = c.rolling(6, min_periods=1).std().fillna(0)

    df["zscore"] = np.where(
        df["roll_std_6"] > 0,
        (c - df["roll_mean_6"]) / df["roll_std_6"],
        0.0,
    )

    return df


def _run_isolation_forest(df: pd.DataFrame) -> pd.DataFrame:
    cols = ["consumption_per_hour", "zscore", "roll_std_2", "roll_std_6", "gap_min"]
    cols = [c for c in cols if c in df.columns]
    X = df[cols].fillna(0).values

    if len(X) < 20:
        df["anomaly"] = False
        df["anomaly_score"] = 0.5
        return df

    X_scaled = StandardScaler().fit_transform(X)
    clf = IsolationForest(
        contamination=IF_CONTAMINATION,
        n_estimators=150,
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_scaled)

    df = df.copy()
    df["anomaly_score"] = clf.score_samples(X_scaled)
    df["anomaly"] = clf.predict(X_scaled) == -1
    return df


def _detect_gaps(df: pd.DataFrame) -> list[dict]:
    df = df.sort_values("timestamp")
    gaps = []
    ts = df["timestamp"].tolist()
    mids = df["meter_id"].tolist()

    for i in range(1, len(ts)):
        gap_min = (ts[i] - ts[i - 1]).total_seconds() / 60
        if gap_min > OUTAGE_GAP_MINUTES:
            missed = max(1, round(gap_min / 30) - 1)
            gaps.append({
                "meter_id": int(mids[i]),
                "start": ts[i - 1].isoformat(),
                "end": ts[i].isoformat(),
                "duration_h": round(gap_min / 60, 2),
                "missed_periods": int(missed),
            })
    return gaps


def _risk_score(feat_df: pd.DataFrame, gaps: list[dict]) -> float:
    n = len(feat_df)
    if n == 0:
        return 0.0

    anomaly_rate = float(feat_df["anomaly"].mean())

    total_expected = n + sum(g["missed_periods"] for g in gaps)
    missed_rate = sum(g["missed_periods"] for g in gaps) / max(total_expected, 1)

    score = 0.60 * anomaly_rate + 0.40 * min(missed_rate * 3, 1.0)
    return round(float(np.clip(score, 0.0, 1.0)), 4)


def analyze_feeder(df: pd.DataFrame) -> dict:
    if df.empty:
        return {
            "status": "NO_DATA", "risk_score": 0.0,
            "total_outages": 0, "total_readings": 0,
            "avg_load": 0.0, "max_load": 0.0, "max_gap_hours": 0.0,
            "anomaly_count": 0, "anomaly_rate": 0.0,
            "anomalies": [], "gaps": [],
        }

    all_feat, all_gaps = [], []

    for _, grp in df.groupby("meter_id"):
        feat = _build_features(grp.copy())
        feat = _run_isolation_forest(feat)
        all_gaps.extend(_detect_gaps(feat))
        all_feat.append(feat)

    feat_df = pd.concat(all_feat, ignore_index=True)

    avg_load = 0.0
    max_load = 0.0
    max_gap_h = max((g["duration_h"] for g in all_gaps), default=0.0)

    anomaly_rows = feat_df[feat_df["anomaly"]].sort_values("anomaly_score").head(50)
    anomalies_out = [
        {
            "meter_id": int(r["meter_id"]),
            "timestamp": r["timestamp"].isoformat(),
            "value": round(float(r["value"]), 3),
            "consumption": round(float(r.get("consumption_per_hour") or 0), 3),
            "zscore": round(float(r.get("zscore") or 0), 3),
            "anomaly_score": round(float(r["anomaly_score"]), 4),
        }
        for _, r in anomaly_rows.iterrows()
    ]

    risk = _risk_score(feat_df, all_gaps)
    status = "CRITICAL" if risk >= 0.65 else "WARNING" if risk >= 0.35 else "OK"

    return {
        "status": status,
        "risk_score": risk,
        "total_outages": len(all_gaps),
        "total_readings": len(feat_df),
        "avg_load": avg_load,
        "max_load": max_load,
        "max_gap_hours": round(max_gap_h, 2),
        "anomaly_count": int(feat_df["anomaly"].sum()),
        "anomaly_rate": round(float(feat_df["anomaly"].mean()), 4),
        "anomalies": anomalies_out,
        "gaps": sorted(all_gaps, key=lambda g: -g["duration_h"])[:20],
    }


def detect_gaps_only(df: pd.DataFrame, gap_threshold_minutes: int = 95) -> list[dict]:
    if df.empty:
        return []
    df = df.sort_values("timestamp")
    gaps = []
    ts_list = df["timestamp"].tolist()
    meter_ids = df["meter_id"].tolist()

    for i in range(1, len(ts_list)):
        gap_min = (ts_list[i] - ts_list[i-1]).total_seconds() / 60
        if gap_min > gap_threshold_minutes:
            missed = max(1, round(gap_min / 30) - 1)
            gaps.append({
                "meter_id": int(meter_ids[i]),
                "start": ts_list[i-1].isoformat(),
                "end": ts_list[i].isoformat(),
                "duration_h": round(gap_min / 60, 2),
                "missed_periods": int(missed),
            })
    return gaps