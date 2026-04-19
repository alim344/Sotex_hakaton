package com.example.sotexhakaton.service;

import com.example.sotexhakaton.dto.OverloadHistory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

@Service
public class OverloadService {




    private final RestTemplate restTemplate = new RestTemplate();
    private final String PYTHON_URL = "http://localhost:8000/history/";

    public List<OverloadHistory> getHistoryFromPython(Integer feederId) {
        String url = PYTHON_URL + feederId;


        OverloadHistory[] response = restTemplate.getForObject(url, OverloadHistory[].class);

        return response != null ? Arrays.asList(response) : Collections.emptyList();
    }



}
