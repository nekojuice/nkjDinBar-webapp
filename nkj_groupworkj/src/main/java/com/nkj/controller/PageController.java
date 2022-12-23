package com.nkj.controller;

import java.util.Arrays;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;

import com.nkj.connection.nkjSocketIO;

@SuppressWarnings("unused")
@Controller
public class PageController {
	
//	@ResponseStatus(value = HttpStatus.OK)
//	@GetMapping(value = "/user/{name}")
//	public void process(@PathVariable String name) {
//
//	}

//	@RequestMapping("/MyFirstPage")
//	public String greeting(@RequestParam(value = "title", required = false, defaultValue = "xiao") String title,
//			Model model) {
//		model.addAttribute("name", title);
//		return "index";
//	}
	
	@RequestMapping("/videoStream")
	public String videoStream() {
		return "videoStream.html";
	}
	
	@RequestMapping("/pi")
	public String PiController() {
		return "PiController.html";
	}
}
