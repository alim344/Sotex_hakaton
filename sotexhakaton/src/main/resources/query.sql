WITH DeltaCalculation AS (
    SELECT
        m.Mid,
        m.Ts,
        (m.Val - LAG(m.Val) OVER (PARTITION BY m.Mid ORDER BY m.Ts)) AS RawDelta
    FROM dbo.MeterReadTfes m
             JOIN dbo.Meters me ON m.Mid = me.Id
             JOIN dbo.Feeders11 f ON f.MeterId = me.Id
    WHERE f.Id = 17
),
     NormalizedData AS (
         SELECT
             d.Ts AS timestamp,
    (d.RawDelta * mt.MultiplierFactor) / 10000.0 AS energy_kwh,
    (f.NameplateRating * 0.45) AS limit_kwh
FROM DeltaCalculation d
    JOIN dbo.Meters mt ON d.Mid = mt.Id
    JOIN dbo.Feeders11 f ON f.MeterId = mt.Id
WHERE d.RawDelta >= 0
  AND d.Ts >= DATEADD(day, -3, (SELECT MAX(Ts) FROM dbo.MeterReadTfes))
    )
SELECT
    timestamp,
    energy_kwh,
    ROUND((energy_kwh / NULLIF(limit_kwh, 0)) * 100, 2) AS load_percent,
    CASE
    WHEN (energy_kwh / NULLIF(limit_kwh, 0)) > 1.0 THEN 'OVERLOAD'
    WHEN (energy_kwh / NULLIF(limit_kwh, 0)) BETWEEN 0.8 AND 1.0 THEN 'STRESSED'
    ELSE 'NORMAL'
END AS status
        FROM NormalizedData
        ORDER BY timestamp DESC;


WITH MaxLoad AS (
    SELECT
        f.Id,
        MAX((m.Val - LAG_VAL) * mt.MultiplierFactor / 10000.0) as PeakPower
    FROM (
             SELECT Mid, Val, LAG(Val) OVER (PARTITION BY Mid ORDER BY Ts) as LAG_VAL FROM dbo.MeterReadTfes
         ) m
             JOIN dbo.Meters mt ON m.Mid = mt.Id
             JOIN dbo.Feeders11 f ON f.MeterId = mt.Id
    GROUP BY f.Id
)
SELECT Id, ROUND(PeakPower / 4.5, 0) as estimated_consumers
FROM MaxLoad
ORDER BY estimated_consumers DESC
