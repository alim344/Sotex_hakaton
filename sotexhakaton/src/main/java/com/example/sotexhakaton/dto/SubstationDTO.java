package com.example.sotexhakaton.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

import java.math.BigDecimal;

@Getter
@Setter
@AllArgsConstructor
public class SubstationDTO {
    private Integer id;
    private String name;
    private BigDecimal latitude;
    private BigDecimal longitude;
    private Integer f11Count;
}
