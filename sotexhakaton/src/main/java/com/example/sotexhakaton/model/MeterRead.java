package com.example.sotexhakaton.model;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "MeterReads")
@Getter
@Setter
public class MeterRead {
    @Id
    private Integer Id;

    private int Mid;
    private float Val;
    private LocalDateTime Ts;
    private int Cid;


}
