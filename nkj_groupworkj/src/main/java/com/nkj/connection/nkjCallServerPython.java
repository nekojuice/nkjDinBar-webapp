package com.nkj.connection;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Arrays;

import io.socket.client.IO;
import io.socket.client.Socket;
import com.nkj.connection.nkjSocketIO;

/**
 * @author nkj
 */
@SuppressWarnings("unused")
public class nkjCallServerPython {
	private IO.Options options = new IO.Options();
	private nkjSocketIO sock = new nkjSocketIO();
	
	public void PythonFileLauncher() {
		String[] arg = new String[] {"python", "D:\\Python\\Workspace\\flask\\J2PyCameraReceiver.py"};
		try {
			Process pr = Runtime.getRuntime().exec(arg);
			BufferedReader in = new BufferedReader(new InputStreamReader(pr.getInputStream()));
			
			String line;
			while ((line = in.readLine()) != null ) {
				System.out.print(line);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		Object[] emit = sock.IO_Emit("http://192.168.137.10:5000", "connectionTest", "cathi");
		System.out.print(Arrays.toString(emit));
	}
	
	

	
}
