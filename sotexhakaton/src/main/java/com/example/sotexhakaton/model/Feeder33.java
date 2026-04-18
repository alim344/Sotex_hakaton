package com.example.sotexhakaton.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(name = "Feeders33")
@Getter
@Setter
public class Feeder33 {

    @Id
    private Integer Id;

    private String Name;
    private int TsId;
    @Column(nullable = false)
    private Boolean IsDeleted;

    private int MeterId;
    private int NameplateRating;



}
