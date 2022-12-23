package com.nkj.connection;

import java.net.URISyntaxException;
import java.util.Arrays;

import io.socket.client.IO;
import io.socket.client.Socket;
import lombok.Getter;
import lombok.Setter;

public class nkjIO {
	private IO.Options options = new IO.Options();
	private Socket socket;

	@Getter
	@Setter
	private String url;
	private String testConnectListener;

	public nkjIO() {
	}

	public nkjIO(String url, String testConnectListener) {
		this.url = url;
		this.testConnectListener = testConnectListener;
	}

	private void ConnectOptionsSetup() {
		options.reconnectionAttempts = 5; // 重試次數 int
		options.reconnectionDelay = 1000; // 重試間格 int ms
		options.timeout = 500; // 判斷為失敗的超時時間 int ms
	}

	public void IOCreateConnection() {
		ConnectOptionsSetup();
		try {
			socket = IO.socket(url, options);
			String msgPrefix = url + ": [" + testConnectListener + "]|>> ";
			socket.on(Socket.EVENT_CONNECT, objects -> System.out.println(msgPrefix + "已建立連線"));
			socket.on(Socket.EVENT_DISCONNECT, objects -> System.out.println(msgPrefix + "連線中斷"));
			socket.on(Socket.EVENT_CONNECT_ERROR, objects -> System.out.println(msgPrefix + "連線失敗"));
			socket.connect();
		} catch (URISyntaxException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public void emit(String listener, String message) {
		String msgPrefix = url + ": [" + listener + "]|>> ";
		socket.emit(listener, message);
		System.out.println(msgPrefix + "[Ja]->[Py]: " + message);
		socket.on(listener, objects -> {
			if (objects != null) {
				System.out.println(msgPrefix + "[Py]->[Ja]: " + Arrays.toString(objects));
			}
		});
	}

}
