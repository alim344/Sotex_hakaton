package com.example.sotexhakaton.service;

import com.example.sotexhakaton.dto.FeederRiskResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.server.ResponseStatusException;

import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class PredictionService {

    private final RestTemplate restTemplate;

    @Value("${prediction.service.url:http://localhost:8000}")
    private String predictionUrl;

    /**
     * Poziva Python /analyze endpoint i vraća rezultat.
     *
     * @param feeder11Id  ID Feeders11 zapisa
     * @param hours       Prozor analize u satima (default 168 = 7 dana)
     * @param useForecast Da li da uključi Prophet/SARIMA predikciju
     * @param horizonH    Koliko sati unapred da predviđa (ako useForecast=true)
     */
    public FeederRiskResponse getFeederRisk(
            Integer feeder11Id,
            Integer hours,
            Boolean useForecast,
            Integer horizonH) {

        String url = predictionUrl + "/analyze";

        Map<String, Object> body = Map.of(
                "feeder11_id",   feeder11Id,
                "hours",         hours,
                "use_forecast",  useForecast,
                "horizon_hours", horizonH
        );

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, Object>> entity = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<FeederRiskResponse> resp = restTemplate.exchange(
                    url, HttpMethod.POST, entity, FeederRiskResponse.class);
            return resp.getBody();

        } catch (HttpClientErrorException.NotFound e) {
            log.warn("Python API: nema podataka za feeder {}", feeder11Id);
            throw new ResponseStatusException(
                    HttpStatus.NOT_FOUND,
                    "Nema podataka za Feeder11 ID=" + feeder11Id);

        } catch (Exception e) {
            log.error("Greška pri pozivu Python API-ja: {}", e.getMessage());
            throw new ResponseStatusException(
                    HttpStatus.SERVICE_UNAVAILABLE,
                    "Prediction servis nije dostupan: " + e.getMessage());
        }
    }

    public FeederRiskResponse getFeederRisk(Integer feeder11Id, Integer hours) {
        return getFeederRisk(feeder11Id, hours, false, 24);
    }
}