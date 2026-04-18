package com.example.sotexhakaton.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

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


    @ManyToMany
    @JoinTable(
            name = "Feeder33Substation",
            joinColumns = @JoinColumn(name = "Feeders33Id"),
            inverseJoinColumns = @JoinColumn(name = "SubstationsId")
    )
    private List<Substations> substations;


}
