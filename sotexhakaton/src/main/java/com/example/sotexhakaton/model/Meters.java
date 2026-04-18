package com.example.sotexhakaton.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Entity
@Table(name = "Meters")
@NoArgsConstructor
@AllArgsConstructor
public class Meters {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "MSN", length = 40)
    private String msn;

    @Column(name = "MultiplierFactor", nullable = false)
    private Double multiplierFactor;

    @OneToMany(mappedBy = "meter")
    private List<MeterReadTfes> meterReadTfes;

//    @OneToMany(mappedBy = "meter")
//    private List<MeterReads> meterReads;
}
