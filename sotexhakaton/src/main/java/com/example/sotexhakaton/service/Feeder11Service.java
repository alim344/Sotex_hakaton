package com.example.sotexhakaton.service;

import com.example.sotexhakaton.model.Feeder11;
import com.example.sotexhakaton.repository.Feeder11Repository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class Feeder11Service {

    @Autowired
    private Feeder11Repository feeder11Repository;

    public List<Feeder11> getFeedersBySubstation(Integer ssId) {
        return feeder11Repository.findBySsId(ssId);
    }

    public List<Feeder11> findAll() {
        return feeder11Repository.findAll();
    }

}
