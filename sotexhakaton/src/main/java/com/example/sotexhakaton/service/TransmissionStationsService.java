package com.example.sotexhakaton.service;

import com.example.sotexhakaton.repository.TransmissionStationsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class TransmissionStationsService {
    @Autowired
    private TransmissionStationsRepository transmissionStationsRepository;
}
