package com.example.sotexhakaton.service;

import com.example.sotexhakaton.repository.SubstationsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class SubstationsService {

    @Autowired
    private SubstationsRepository substationsRepository;
}
