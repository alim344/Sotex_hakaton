package com.example.sotexhakaton.service;

import com.example.sotexhakaton.model.Substations;
import com.example.sotexhakaton.model.TransmissionStations;
import com.example.sotexhakaton.repository.TransmissionStationsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class TransmissionStationsService {
    @Autowired
    private TransmissionStationsRepository transmissionStationsRepository;

    public List<TransmissionStations> findAll() {
        return transmissionStationsRepository.findAll();
    }
}
