package com.example.sotexhakaton.service;

import com.example.sotexhakaton.dto.OverloadHistory;

import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

@Service
public class OverloadService {


    private final RestTemplate restTemplate = new RestTemplate();
    private final String PYTHON_URL = "http://localhost:8000/history/";

    @Cacheable(value = "feederHistory", key = "#feederId", unless = "#result.isEmpty()")
    public List<OverloadHistory> getHistoryFromPython(Integer feederId) {
        String url = PYTHON_URL + feederId;

        try {
            OverloadHistory[] response = restTemplate.getForObject(url, OverloadHistory[].class);
            return response != null ? Arrays.asList(response) : Collections.emptyList();
        }catch (Exception e){
            System.err.println("Greška prilikom pozivanja Pythona: " + e.getMessage());
            return Collections.emptyList();
        }
    }



}
