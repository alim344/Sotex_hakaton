package com.example.sotexhakaton.controller;

import com.example.sotexhakaton.dto.FeederRiskResponse;
import com.example.sotexhakaton.service.PredictionService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/prediction")
@RequiredArgsConstructor
public class PredictionController {

    private final PredictionService predictionService;

    /**
     * Detaljna analiza jednog Feeder11.
     *
     * GET /api/prediction/feeder11/{id}
     *   ?hours=168          — prozor analize (default: 7 dana)
     *   &forecast=false     — uključi Prophet/SARIMA predikciju (sporije)
     *   &horizon=24         — koliko sati unapred da predviđa
     *
     * Primeri:
     *   GET /api/prediction/feeder11/5
     *   GET /api/prediction/feeder11/5?hours=72&forecast=true&horizon=48
     */
    @GetMapping("/feeder11/{id}")
    public ResponseEntity<FeederRiskResponse> getFeederRisk(
            @PathVariable Integer id,
            @RequestParam(defaultValue = "168")  Integer hours,
            @RequestParam(defaultValue = "false") Boolean forecast,
            @RequestParam(defaultValue = "24")   Integer horizon) {

        return ResponseEntity.ok(
                predictionService.getFeederRisk(id, hours, forecast, horizon));
    }
}