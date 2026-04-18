package com.example.sotexhakaton.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class FeederRiskResponse {

    @JsonProperty("feeder11_id")
    private Integer feeder11Id;

    private String status;        // OK / WARNING / CRITICAL

    @JsonProperty("risk_score")
    private Double riskScore;     // 0.0 – 1.0

    @JsonProperty("total_outages")
    private Integer totalOutages;

    @JsonProperty("total_readings")
    private Integer totalReadings;

    @JsonProperty("avg_load")
    private Double avgLoad;

    @JsonProperty("max_load")
    private Double maxLoad;

    @JsonProperty("from_cache")
    private Boolean fromCache;

    @JsonProperty("anomalies_found")
    private Integer anomaliesFound;

    @JsonProperty("prediction")
    private String prediction;
}