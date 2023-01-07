package com.nkj.test;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

import com.nkj.connection.nkjSocketIO;

@SuppressWarnings("unused")
public class PythonTest {
	

	
	public static void main(String[] args) {

		try {
			//Runtime.getRuntime().exec("python script.py arg1 arg2");
			//Process pr = Runtime.getRuntime().exec("python D:/Eclipse/Workspace/JavaEE/nkj_groupworkj/src/main/java/com/nkj/socketio/test/test.py");
			String[] arg = new String[] {"python", "D:\\Python\\Workspace\\flask\\zmqClientTest.py"};
			Process pr = Runtime.getRuntime().exec(arg);
//			BufferedReader in = new BufferedReader(new InputStreamReader(pr.getInputStream()));
//			String line;
//			
//			while ((line = in.readLine()) != null ) {
//				System.out.print(line);
//			}
//			System.out.print(in.readLine());
			
			nkjSocketIO nkjSocketIO = new nkjSocketIO();
			nkjSocketIO.PiCameraSwitch("cat", "dog", true);
		} catch (IOException e) {

			e.printStackTrace();
		}
	}
	

}
