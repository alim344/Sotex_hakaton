package com.example.sotexhakaton.controller;

import com.example.sotexhakaton.dto.Feeder11SimpleDTO;
import com.example.sotexhakaton.model.Feeder11;
import com.example.sotexhakaton.service.Feeder11Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/feeders")
@CrossOrigin(origins = "http://localhost:5173")
public class Feeder11Controller {

    @Autowired
    private Feeder11Service feeder11Service;

  /*  @GetMapping("/by-substation")
    public ResponseEntity<Map<Integer, List<Feeder11>>> getFeedersGroupedBySubstation() {
        List<Feeder11> allFeeders = feeder11Service.findAll();

        Map<Integer, List<Feeder11>> grouped = allFeeders.stream()
                .filter(f -> f.getSsId() != null)
                .collect(Collectors.groupingBy(Feeder11::getSsId));

        return ResponseEntity.ok(grouped);
    } */

    @GetMapping("/by-substation/{ssId}")
    public ResponseEntity<List<Feeder11SimpleDTO>> getFeedersBySubstation(@PathVariable Integer ssId) {
        List<Feeder11> feeders = feeder11Service.getFeedersBySubstation(ssId);

        List<Feeder11SimpleDTO> result = feeders.stream()
                .map(f -> new Feeder11SimpleDTO(f.getId(), f.getName()))
                .collect(Collectors.toList());

        System.out.println("Feeders za SS " + ssId + ": " + result.size()); // LOG
        result.forEach(f -> System.out.println("  - " + f.getId() + ": " + f.getName()));

        return ResponseEntity.ok(result);
    }

    @GetMapping("/all")
    public ResponseEntity<List<Feeder11SimpleDTO>> getAllFeeders() {
        List<Feeder11> feeders = feeder11Service.findAll();

        List<Feeder11SimpleDTO> result = feeders.stream()
                .map(f -> new Feeder11SimpleDTO(f.getId(), f.getName()))
                .collect(Collectors.toList());

        return ResponseEntity.ok(result);
    }
}