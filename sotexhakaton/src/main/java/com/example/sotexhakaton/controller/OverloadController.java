package com.example.sotexhakaton.controller;

import com.example.sotexhakaton.dto.OverloadHistory;
import com.example.sotexhakaton.service.OverloadService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/overload")
public class OverloadController {

    @Autowired
    private OverloadService overloadService;

    @GetMapping("/gethistory/{id}")
    public ResponseEntity<List<OverloadHistory>> getHistory(@PathVariable Integer id) {
        return ResponseEntity.ok(overloadService.getHistoryFromPython(id));
    }


}
