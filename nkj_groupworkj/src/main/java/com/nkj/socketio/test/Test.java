package com.nkj.socketio.test;

import io.socket.client.IO;
import io.socket.client.Socket;


public class Test {

	public static void main(String[] args) {

		String url = "http://127.0.0.1:5000";
		try {
			IO.Options options = new IO.Options();
			//options.transports = new String[] { "websocket" };
			// 失敗重試次數
			options.reconnectionAttempts = 10;
			// 失敗重連的時間間隔
			options.reconnectionDelay = 1000;
			// 連線超時時間(ms)
			options.timeout = 500;
			final Socket socket = IO.socket(url, options);
			// 監聽自定義msg事件'
			socket.emit("msg", "123");
//			socket.on("msg", objects -> System.out.println("client: 收到msg->" + Arrays.toString(objects)));
//			// 監聽自定義訂閱事件
//			socket.on("sub", objects -> System.out.println("client: " + "訂閱成功，收到反饋->" + Arrays.toString(objects)));
//			socket.on(Socket.EVENT_CONNECT, objects -> {
//				socket.emit("sub", "我是訂閲物件");
//				System.out.println("client: " + "連線成功");
//			});
			socket.on(Socket.EVENT_CONNECT, objects -> System.out.println("client: " + "已建立連線"));
			socket.on(Socket.EVENT_DISCONNECT, objects -> System.out.println("client: " + "連線中斷"));
			socket.on(Socket.EVENT_CONNECT_ERROR, objects -> System.out.println("client: " + "連線失敗"));
			socket.connect();
		} catch (Exception ex) {
			ex.printStackTrace();
		}

	}

}
