package com.example.sotexhakaton.dto;

import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
public class OverloadHistory {

        private LocalDateTime timestamp;
        private Double energy_kwh;
        private Double load_percent;
        private String status;

        public OverloadHistory() {}

}
