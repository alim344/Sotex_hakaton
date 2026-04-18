package com.example.sotexhakaton.repository;

import com.example.sotexhakaton.model.Feeder11;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface Feeder11Repository extends JpaRepository<Feeder11,Long> {
    List<Feeder11> findBySsIdNotNull();

    List<Feeder11> findBySsId(Integer ssId);
}
