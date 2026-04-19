package com.example.sotexhakaton.controller;


import com.example.sotexhakaton.dto.SubstationDTO;
import com.example.sotexhakaton.model.Substations;
import com.example.sotexhakaton.service.SubstationsService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/substations")
@CrossOrigin(origins = "http://localhost:5173")
public class SubstationsController {
    @Autowired
    private SubstationsService substationsService;

    @GetMapping("/all")
    public ResponseEntity<List<SubstationDTO>> getAllSubstations() {
        List<Substations> substations = substationsService.findAll();

        List<SubstationDTO> result = substations.stream()
                .filter(s -> s.getLatitude() != null && s.getLongitude() != null)
                .map(s -> {
                    // Izračunaj broj F11 za ovu stanicu
                    Integer f11Count = substationsService.getF11CountBySsId(s.getId());
                    return new SubstationDTO(
                            s.getId(),
                            s.getName(),
                            s.getLatitude(),
                            s.getLongitude(),
                            f11Count  // NOVO polje
                    );
                })
                .collect(Collectors.toList());

        return ResponseEntity.ok(result);
    }
}
