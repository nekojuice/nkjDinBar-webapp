package com.nkj.socketio.test;

import java.io.File;
import java.io.IOException;

import us.monoid.web.Resty;

public class FileDownloader2 {

	@SuppressWarnings("unused")
	public static void main(String[] args) {
		Resty r = new Resty();
		try {
			File f = r.bytes("https://s.yimg.com/ny/api/res/1.2/MVNglMuGchD1wzV7B9kEug--/YXBwaWQ9aGlnaGxhbmRlcjt3PTk2MDtoPTYzODtjZj13ZWJw/https://media.zenfs.com/en/cna.com.tw/19043df38fb9f4af3af80089320021d8").
					  save(File.createTempFile("google", ".png"));
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}

}
