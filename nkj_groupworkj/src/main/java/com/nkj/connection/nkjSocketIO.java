package com.nkj.connection;

import java.net.URISyntaxException;
import java.util.Arrays;

import io.socket.client.IO;
import io.socket.client.Socket;

/**
 * @author nkj
 */
public class nkjSocketIO {
	private IO.Options options = new IO.Options();

	private void PiConnection() {
		options.reconnectionAttempts = 10;
		options.reconnectionDelay = 1000;
		options.timeout = 500;
	}

	/**
	 * Control raspi Camera on off.
	 * 
	 * @param url      (String)>>>e.g.: http://192.168.137.10:5000
	 * @param listener (String)>>>The listener name on raspi python controller.
	 * @param onoff    (Boolean)>>>Switch ON or OFF, input true or false.
	 * @return No return value.
	 */
	public void PiCameraSwitch(String url, String listener, Boolean onoff) {
		try {
			PiConnection();
			final Socket socket = IO.socket(url, options);
			socket.emit(listener, onoff);
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

	/**
	 * Listener.
	 * 
	 * @param url      (String)>>>e.g.: http://192.168.137.10:5000
	 * @param listener (String)>>>The listener name to catch emit.
	 * @return No return value.
	 */
	public void PiListener(String url, String listener) {
		try {
			PiConnection();
			final Socket socket = IO.socket(url, options);
			socket.on("sub", objects -> {
				System.out.println(Arrays.toString(objects));
			});
		} catch (URISyntaxException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}
	
	private Object[] message_IO_Emit;
	/**
	 * Socket IO Emitter.
	 * 
	 * @param url      (String)>>>e.g.: http://192.168.137.10:5000
	 * @param listener (String)>>>The listener name on raspi python controller.
	 * @param message  (String)>>>String to emit.
	 * @return Object[], use Arrays.toString(IO_Emit(args)) convert to string.
	 */
	public Object[] IO_Emit(String url, String listener, String message) {
		try {
			final Socket socket = IO.socket(url, options);
			socket.emit(listener, message);
			System.out.println(listener + "[Ja]->[Py]: " + message);
			socket.on(listener, objects -> {
				if (objects != null) {
					System.out.println(listener + "[Py]->[Ja]: " + Arrays.toString(objects));
				}
				message_IO_Emit = objects;
			});
			socket.on(Socket.EVENT_CONNECT, objects -> System.out.println("IO_Emit: " + "已建立連線"));
			socket.on(Socket.EVENT_DISCONNECT, objects -> System.out.println("IO_Emit: " + "連線中斷"));
			socket.on(Socket.EVENT_CONNECT_ERROR, objects -> System.out.println("IO_Emit: " + "連線失敗"));
			socket.connect();
		} catch (Exception ex) {
			ex.printStackTrace();
		}
		return message_IO_Emit;
	}
	
	private Object[] message_IO_On;
	/**
	 * Socket IO listener.
	 * 
	 * @param url      (String)>>>e.g.: http://192.168.137.10:5000
	 * @param listener (String)>>>The listener name on raspi python controller.
	 * @return Object[], use Arrays.toString(IO_On(args)) convert to string.
	 */
	public Object[] IO_On(String url, String listener) {
		try {
			final Socket socket = IO.socket(url, options);
			socket.on(listener, objects -> {
					message_IO_On = objects;
			});
			socket.on(Socket.EVENT_CONNECT, objects -> System.out.println("IO_On: " + "已建立連線"));
			socket.on(Socket.EVENT_DISCONNECT, objects -> System.out.println("IO_On: " + "連線中斷"));
			socket.on(Socket.EVENT_CONNECT_ERROR, objects -> System.out.println("IO_On: " + "連線失敗"));
			socket.connect();
		} catch (Exception ex) {
			ex.printStackTrace();
		}
		return message_IO_On;
	}

}
