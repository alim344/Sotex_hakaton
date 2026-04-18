package com.example.sotexhakaton.model;

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(name = "Feeders11")
@Getter @Setter
public class Feeder11 {

    @Id
    private Integer Id;


    private String Name;

    private int SsId;

    private int MeterId;

    private int Feeder33Id;

    private int NameplateRating;

    private int TsId;



}
