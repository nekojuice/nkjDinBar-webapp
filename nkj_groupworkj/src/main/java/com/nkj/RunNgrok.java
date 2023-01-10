package com.nkj;

import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.ApplicationListener;
import org.springframework.stereotype.Component;

import com.github.alexdlaird.ngrok.NgrokClient;
import com.github.alexdlaird.ngrok.protocol.CreateTunnel;
import com.github.alexdlaird.ngrok.protocol.Proto;
import com.github.alexdlaird.ngrok.protocol.Tunnel;


@Component
public class RunNgrok implements ApplicationListener<ApplicationReadyEvent> {

public static String javaPublicUrl;
//private String pythonPublicUrl;

	@Override
	public void onApplicationEvent(ApplicationReadyEvent event) {
	    System.out.println("ngrok starting...");
	    final NgrokClient ngrokClient = new NgrokClient.Builder().build();
	    //final Tunnel httpTunnel = ngrokClient.connect();
	    final CreateTunnel javaCreateTunnel = new CreateTunnel.Builder()
	    		.withProto(Proto.HTTP)
	    		.withAddr(8080)
	    		.build();
//	    final CreateTunnel pythonCreateTunnel = new CreateTunnel.Builder()
//	    		.withProto(Proto.HTTP)
//	    		.withAddr(5000)
//	    		.build();
	    
	    final Tunnel javaTunnel = ngrokClient.connect(javaCreateTunnel);
//	    final Tunnel pythonTunnel = ngrokClient.connect(pythonCreateTunnel);
	    
	    System.out.println(javaTunnel.getPublicUrl());
	    javaPublicUrl = javaTunnel.getPublicUrl();
//	    System.out.println(pythonTunnel.getPublicUrl());
//	    this.pythonPublicUrl = "python(5000): " + pythonTunnel.getPublicUrl();
	}
	
}
