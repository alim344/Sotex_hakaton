package com.example.sotexhakaton.service;

import com.example.sotexhakaton.model.DistributionSubstation;
import com.example.sotexhakaton.repository.DistributionSubstationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class DistributionSubstationService {
    @Autowired
    private DistributionSubstationRepository distributionSubstationRepository;

    public List<DistributionSubstation> findAll() {
        return distributionSubstationRepository.findAll();
    }
}
