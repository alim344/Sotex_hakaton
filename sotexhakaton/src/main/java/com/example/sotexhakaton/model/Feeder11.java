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

    private Integer SsId;

    private Integer MeterId;

    private Integer Feeder33Id;

    private Integer NameplateRating;

    private Integer TsId;



}
