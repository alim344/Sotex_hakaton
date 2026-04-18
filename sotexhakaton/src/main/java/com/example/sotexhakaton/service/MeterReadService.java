package com.example.sotexhakaton.service;

import com.example.sotexhakaton.repository.MeterReadRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class MeterReadService {

    @Autowired
    private MeterReadRepository meterReadRepository;
}
