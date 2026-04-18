package com.example.sotexhakaton.controller;

import com.example.sotexhakaton.model.Feeder11;
import com.example.sotexhakaton.service.Feeder11Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

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
}