package com.example.sotexhakaton.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "MeterReadTfes")
@NoArgsConstructor
@AllArgsConstructor
public class MeterReadTfes {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "Mid", nullable = false)
    private Integer mid;

    @Column(name = "Val", nullable = false)
    private Double val;

    @Column(name = "Ts", nullable = false)
    private LocalDateTime ts;
}
