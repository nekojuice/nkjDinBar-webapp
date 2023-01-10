package com.nkj.controller;

import java.net.URISyntaxException;
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
	public String login(Model model) {
		String url = RunNgrok.javaPublicUrl;
		model.addAttribute("publicURL", url);
		return "login";
	}

	@RequestMapping("/contact")
	public String contact() {
		return "contact.html";
	}
	
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
	
//	@RequestMapping("/videoStream")
//	public String videoStream() {
//		return "videoStream.html";
//	}
	
//	@RequestMapping("/pi")
//	public String PiController() {
//		return "PiController.html";
//	}
//	
//	@RequestMapping("/t1")
//	public String test1() {
//		Socket socket;
//		try {
//			socket = IO.socket("http://127.0.0.1:8080/t1");
//			socket.on("camera_switch", listener ->  {
//				System.out.println(Arrays.toString(listener));
//			});
//		} catch (URISyntaxException e) {

//			e.printStackTrace();
//		}
//		String url = "http://127.0.0.1:8080/";
//		String listener = "test1";
//		IO.Options options = new IO.Options();
//		options.reconnectionAttempts = 5;	//重試次數 int
//		options.reconnectionDelay = 1000;	//重試間格 int ms
//		options.timeout = 500;				//判斷為失敗的超時時間 int ms
//		try {
//			final Socket socket = IO.socket(url, options);
//			String msgPrefix = url + ": [" + listener + "]|>> ";
//			socket.on(listener, objects -> System.out.println(msgPrefix + Arrays.toString(objects)));  // io.on here
//			
//			socket.on(Socket.EVENT_CONNECT, objects -> System.out.println(msgPrefix + "已建立連線"));
//			socket.on(Socket.EVENT_DISCONNECT, objects -> System.out.println(msgPrefix + "連線中斷"));
//			socket.on(Socket.EVENT_CONNECT_ERROR, objects -> System.out.println(msgPrefix + "連線失敗"));
//			socket.connect();
//		} catch (URISyntaxException e) {

//			e.printStackTrace();
//		}
//		return "PiController.html";
//	}
}
