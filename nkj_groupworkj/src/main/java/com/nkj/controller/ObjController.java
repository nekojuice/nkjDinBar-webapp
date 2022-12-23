package com.nkj.controller;

import java.util.Arrays;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.nkj.connection.nkjSocketIO;

@SuppressWarnings("unused")
@RestController
public class ObjController {
	
//	@RequestMapping("/videoStream")
//	public ModelAndView videoStream() {
//		ModelAndView mav = new ModelAndView();
//		mav.setViewName("videoStream.html");
//		return mav;
//	}
	
	@RequestMapping("/test")
	public String PiController() {
		nkjSocketIO sock = new nkjSocketIO();
		Object[] emit = sock.IO_Emit("http://localhost:5000", "connectionTest", "cathi");
		try {
			Thread.sleep(1000);
		} catch (Exception e) {
		}
		
		System.out.println(Arrays.toString(emit));
		return "cathi";
		//return "PiController.html";
	}
	
	
}
