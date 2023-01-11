package com.nkj.controller;

import java.net.URISyntaxException;
import java.util.Arrays;
import java.util.Optional;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;

import com.nkj.RunNgrok;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.client.Url;

@SuppressWarnings("unused")
@Controller
public class PageController {

	@RequestMapping("/")
	public String index() {
		return "index.html";
	}
	
	@RequestMapping("/login")
	public String handlelogin(Model model, @RequestParam("message") Optional<String> attr) {
		if (attr.isEmpty())
			model.addAttribute("message", "");

		else {
			model.addAttribute("message", attr.get());
		}
		return "login.html";
	}

	@RequestMapping("/contact")
	public String contact() {
		return "contact.html";
	}
	
	@RequestMapping("/signin")
	public String handlesignin(Model model, @RequestParam("message") Optional<String> attr) {
		if (attr.isEmpty())
			model.addAttribute("message", "");

		else {
			model.addAttribute("message", attr.get());

		}
		return "signin.html";
	}
}
