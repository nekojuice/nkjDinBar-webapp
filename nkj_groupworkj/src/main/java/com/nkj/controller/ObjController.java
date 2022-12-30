package com.nkj.controller;

import java.net.URISyntaxException;
import java.util.Arrays;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.ModelAndView;

import io.socket.client.IO;
import io.socket.client.Socket;
import io.socket.emitter.Emitter;

@SuppressWarnings("unused")
@RestController
public class ObjController {

//	@RequestMapping("/")
//	public ModelAndView index() {
//		ModelAndView mav = new ModelAndView();
//		mav.setViewName("index.html");
//		return mav;
//	}
	
//	@RequestMapping("/videoStream")
//	public ModelAndView videoStream() {
//		ModelAndView mav = new ModelAndView();
//		mav.setViewName("videoStream.html");
//		return mav;
//	}

//	@RequestMapping("/test")
//	public String PiController() {
//		Socket socket;
//		try {
//			socket = IO.socket("http://127.0.0.1:8080/socket.io/");
//			socket.on("camera_switch", listener ->  {
//				System.out.println(Arrays.toString(listener));
//			});
//		} catch (URISyntaxException e) {

//			e.printStackTrace();
//		}
		
		
//		Object[] emit = sock.IO_Emit("http://localhost:8080", "connectionTest", "cathi");
//		try {
//			Thread.sleep(1000);
//		} catch (Exception e) {
//		}

//		System.out.println(Arrays.toString(emit));
//		return "cathi";
		// return "PiController.html";
//	}

}
