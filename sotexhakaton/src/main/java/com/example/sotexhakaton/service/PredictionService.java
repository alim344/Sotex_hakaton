package com.example.sotexhakaton.service;

import com.example.sotexhakaton.dto.FeederRiskResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class PredictionService {

    private final RestTemplate restTemplate;

    @Value("${prediction.service.url:http://localhost:8000}")
    private String predictionUrl;

    public FeederRiskResponse getFeederRisk(Integer feeder11Id) {
        String url = predictionUrl + "/predict";
        Map<String, Integer> requestBody = Map.of("feeder11_id", feeder11Id);
        return restTemplate.postForObject(url, requestBody, FeederRiskResponse.class);
    }
}