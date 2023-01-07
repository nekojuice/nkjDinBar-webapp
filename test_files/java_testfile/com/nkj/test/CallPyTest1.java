package com.nkj.test;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Arrays;

import com.fasterxml.jackson.annotation.JsonTypeInfo.Id;
import com.nkj.connection.nkjSocketIO;

@SuppressWarnings("unused")
public class CallPyTest1 {

	public static void main(String[] args) {

		nkjSocketIO sock = new nkjSocketIO();

//		String[] arg = new String[] { "python", "D:\\Python\\Workspace\\flask\\J2PyCameraReceiver.py" };
//		try {
//			Process pr = Runtime.getRuntime().exec(arg);
//			BufferedReader in = new BufferedReader(new InputStreamReader(pr.getInputStream()));
//
//			String line;
//			while ((line = in.readLine()) != null) {
//				System.out.println(line);
//				break;
//			}
//		} catch (IOException e) {
//			e.printStackTrace();
//		}
		
		
		Object[] emit = sock.IO_Emit("http://localhost:5000", "connectionTest", "cathi");
		try {
			Thread.sleep(1000);
		} catch (Exception e) {

		}
		
		System.out.println(Arrays.toString(emit));

	}

}
