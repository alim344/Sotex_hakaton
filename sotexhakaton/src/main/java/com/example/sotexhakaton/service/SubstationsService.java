package com.example.sotexhakaton.service;

import com.example.sotexhakaton.model.Substations;
import com.example.sotexhakaton.repository.Feeder11Repository;
import com.example.sotexhakaton.repository.SubstationsRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SubstationsService {

    @Autowired
    private SubstationsRepository substationsRepository;

    @Autowired
    private Feeder11Repository feeder11Repository;

    public List<Substations> findAll() {
        return substationsRepository.findAll();
    }


    public Integer getF11CountBySsId(Integer ssId) {
        return feeder11Repository.countBySsId(ssId);
    }

}
