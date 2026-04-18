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

    @GetMapping("/feeder11/{id}")
    public ResponseEntity<FeederRiskResponse> getFeederRisk(@PathVariable Integer id,
                                                            @RequestParam(defaultValue = "24") Integer hours) {
        return ResponseEntity.ok(predictionService.getFeederRisk(id));
    }
}