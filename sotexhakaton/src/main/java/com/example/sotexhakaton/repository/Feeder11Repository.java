package com.example.sotexhakaton.repository;

import com.example.sotexhakaton.model.Feeder11;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface Feeder11Repository extends JpaRepository<Feeder11,Long> {

    @Query("SELECT COUNT(f) FROM Feeder11 f WHERE f.SsId = :ssId")
    Integer countBySsId(@Param("ssId") Integer ssId);

    @Query("SELECT f FROM Feeder11 f WHERE f.SsId = :ssId")
    List<Feeder11> findBySsId(@Param("ssId") Integer ssId);
}
