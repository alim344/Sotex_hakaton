package com.example.sotexhakaton.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

@Entity
@Table(name = "DistributionSubstation")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DistributionSubstation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "Id")
    private Integer Id;

    @Column(name = "Name", length = 100)
    private String name;

    @Column(name = "MeterId")
    private Integer meterId;

    @Column(name = "Feeder11Id")
    private Integer feeder11Id;

    @Column(name = "Feeder33Id")
    private Integer feeder33Id;

    @Column(name = "NameplateRating")
    private Integer nameplateRating;

    @Column(name = "Latitude", precision = 10, scale = 7)
    private BigDecimal latitude;

    @Column(name = "Longitude", precision = 10, scale = 7)
    private BigDecimal longitude;
}