package com.example.sotexhakaton.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(name = "Channels")
@Getter @Setter
public class Channel {

    @Id
    private Integer Id;


    private String Name;


    private String Unit;


}
