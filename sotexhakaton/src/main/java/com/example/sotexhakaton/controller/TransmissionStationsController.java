package com.example.sotexhakaton.controller;

import com.example.sotexhakaton.model.TransmissionStations;
import com.example.sotexhakaton.service.TransmissionStationsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/transmission-stations")
@CrossOrigin(origins = "http://localhost:5173")
public class TransmissionStationsController {

    @Autowired
    private TransmissionStationsService transmissionStationsService;

    @GetMapping("/all")
    public ResponseEntity<List<TransmissionStations>> getAll() {
        List<TransmissionStations> stations = transmissionStationsService.findAll();
        return ResponseEntity.ok(stations);
    }

}
