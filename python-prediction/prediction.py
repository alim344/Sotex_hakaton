from __future__ import annotations

import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

RESAMPLE_FREQ   = "30min"
PERIODS_PER_DAY = 48
MIN_ROWS        = 48
HIGH_LOAD_PCT   = 0.90


def _prepare_series(df: pd.DataFrame) -> tuple[pd.Series, float]:
    nameplate = float(df["nameplate_rating"].median())
    if nameplate <= 0:
        nameplate = 1.0

    parts = []
    for _, grp in df.groupby("meter_id"):
        g = grp.sort_values("timestamp").copy()
        g["consumption"] = g["value"].diff()
        g.loc[g["consumption"] < 0, "consumption"] = np.nan

        gap_min = g["timestamp"].diff().dt.total_seconds().div(60).fillna(30).clip(lower=1)
        g["consumption_per_hour"] = g["consumption"] / gap_min * 60
        g = g.dropna(subset=["consumption_per_hour"])
        parts.append(g.set_index("timestamp")["consumption_per_hour"])

    if not parts:
        return pd.Series(dtype=float), nameplate

    combined = pd.concat(parts).groupby(level=0).sum().sort_index()
    series   = combined.resample(RESAMPLE_FREQ).interpolate(method="time")
    return series, nameplate


def _sarima(series: pd.Series, steps: int) -> np.ndarray | None:
    try:
        from statsmodels.tsa.statespace.sarimax import SARIMAX
    except ImportError:
        return None

    s = series.iloc[-2000:]

    try:
        fit = SARIMAX(
            s,
            order=(1, 1, 1),
            seasonal_order=(1, 0, 1, PERIODS_PER_DAY),
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(disp=False, maxiter=50)

        pred = fit.get_forecast(steps=steps)
        ci   = pred.conf_int(alpha=0.10)
        return np.column_stack([
            pred.predicted_mean.values,
            ci.iloc[:, 0].values,
            ci.iloc[:, 1].values,
        ])
    except Exception:
        return None


def _naive(series: pd.Series, future_idx: pd.DatetimeIndex) -> np.ndarray:
    std = float(series.std()) if len(series) > 1 else 0.0
    preds = []
    for ts in future_idx:
        mask = (series.index.hour == ts.hour) & (series.index.dayofweek == ts.dayofweek)
        val  = float(series[mask].mean()) if mask.any() else float(series.mean())
        preds.append(val)
    lo = [p - 1.64 * std for p in preds]
    hi = [p + 1.64 * std for p in preds]
    return np.column_stack([preds, lo, hi])


def forecast_feeder(df: pd.DataFrame, horizon_hours: int = 24) -> dict:
    empty = {
        "forecast_points": [], "predicted_peak_load": 0.0,
        "high_risk_windows": [], "method_used": "none",
        "horizon_hours": horizon_hours,
    }

    if df.empty:
        return empty

    series, nameplate = _prepare_series(df)

    if len(series) < MIN_ROWS:
        return empty

    steps      = horizon_hours * 2
    last_ts    = series.index[-1]
    future_idx = pd.date_range(start=last_ts, periods=steps + 1, freq=RESAMPLE_FREQ)[1:]

    result = _sarima(series, steps)
    method = "sarima" if result is not None else "naive"
    if result is None:
        result = _naive(series, future_idx)

    points = []
    for i, ts in enumerate(future_idx):
        yhat = max(float(result[i, 0]), 0.0)
        ylo  = max(float(result[i, 1]), 0.0)
        yhi  = max(float(result[i, 2]), 0.0)
        lp   = min(yhat / nameplate, 9.99) if nameplate > 0 else 0.0
        points.append({
            "timestamp":       ts.isoformat(),
            "predicted_value": round(yhat, 3),
            "lower_bound":     round(ylo,  3),
            "upper_bound":     round(yhi,  3),
            "load_pct":        round(lp,   4),
            "high_risk":       lp >= HIGH_LOAD_PCT,
        })

    peak_load = max(p["load_pct"] for p in points)

    windows, in_win, win_start = [], False, None
    for p in points:
        if p["high_risk"] and not in_win:
            in_win, win_start = True, p["timestamp"]
        elif not p["high_risk"] and in_win:
            in_win = False
            windows.append({"start": win_start, "end": p["timestamp"]})
    if in_win:
        windows.append({"start": win_start, "end": points[-1]["timestamp"]})

    return {
        "forecast_points":     points,
        "predicted_peak_load": round(peak_load, 4),
        "high_risk_windows":   windows,
        "method_used":         method,
        "horizon_hours":       horizon_hours,
    }