package com.example.sotexhakaton.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
@Data
@NoArgsConstructor
@AllArgsConstructor
public class FeederRiskResponse {

    @JsonProperty("feeder11_id")
    private Integer feeder11Id;

    private String status;

    @JsonProperty("risk_score")
    private Double riskScore;

    @JsonProperty("from_cache")
    private Boolean fromCache;

    @JsonProperty("total_readings")
    private Integer totalReadings;

    @JsonProperty("anomaly_count")
    private Integer anomalyCount;

    @JsonProperty("anomaly_rate")
    private Double anomalyRate;

    @JsonProperty("total_outages")
    private Integer totalOutages;

    @JsonProperty("avg_load")
    private Double avgLoad;

    @JsonProperty("max_load")
    private Double maxLoad;

    @JsonProperty("max_gap_hours")
    private Double maxGapHours;

    @JsonProperty("anomalies")
    private List<AnomalyPoint> anomalies;

    @JsonProperty("gaps")
    private List<GapEvent> gaps;

    @JsonProperty("forecast_points")
    private List<ForecastPoint> forecastPoints;

    @JsonProperty("predicted_peak_load")
    private Double predictedPeakLoad;

    @JsonProperty("high_risk_windows")
    private List<HighRiskWindow> highRiskWindows;

    @JsonProperty("method_used")
    private String methodUsed;

    @JsonProperty("horizon_hours")
    private Integer horizonHours;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class AnomalyPoint {
        @JsonProperty("meter_id")      private Integer meterId;
        @JsonProperty("timestamp")     private String  timestamp;
        @JsonProperty("value")         private Double  value;
        @JsonProperty("zscore")        private Double  zscore;
        @JsonProperty("anomaly_score") private Double anomalyScore;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class GapEvent {
        @JsonProperty("meter_id")    private Integer meterId;
        @JsonProperty("start")       private String  start;
        @JsonProperty("end")         private String  end;
        @JsonProperty("duration_h")  private Double  durationH;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ForecastPoint {
        @JsonProperty("timestamp")        private String  timestamp;
        @JsonProperty("predicted_value")  private Double  predictedValue;
        @JsonProperty("lower_bound")      private Double  lowerBound;
        @JsonProperty("upper_bound")      private Double  upperBound;
        @JsonProperty("load_pct")         private Double  loadPct;
        @JsonProperty("high_risk")        private Boolean highRisk;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class HighRiskWindow {
        @JsonProperty("start") private String start;
        @JsonProperty("end")   private String end;
    }
}