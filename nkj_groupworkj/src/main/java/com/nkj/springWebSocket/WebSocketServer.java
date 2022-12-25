package com.nkj.springWebSocket;

import java.io.IOException;
import java.util.concurrent.CopyOnWriteArraySet;

import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

import jakarta.websocket.OnClose;
import jakarta.websocket.OnError;
import jakarta.websocket.OnMessage;
import jakarta.websocket.OnOpen;
import jakarta.websocket.Session;
import jakarta.websocket.server.PathParam;
import jakarta.websocket.server.ServerEndpoint;
import lombok.extern.slf4j.Slf4j;

@Component
@Slf4j
@Service
@ServerEndpoint("/websocket/{sid}")
public class WebSocketServer {
    //靜態變量，用來記錄當前在線連接數。應該把它設計成線程安全的。
    private static int onlineCount = 0;
    //concurrent包的線程安全Set，用來存放每個客戶端對應的MyWebSocket對象。
    private static CopyOnWriteArraySet<WebSocketServer> webSocketSet = new CopyOnWriteArraySet<WebSocketServer>();

    //與某個客戶端的連接會話，需要通過它來給客戶端發送數據
    private Session session;

    //接收sid
    private String sid = "";

    /**
     * 連接建立成功調用的方法
     */
    @OnOpen
    public void onOpen(Session session, @PathParam("sid") String sid) {
        this.session = session;
        webSocketSet.add(this);     //加入set中
        this.sid = sid;
        addOnlineCount();           //在線數加1
        try {
            sendMessage("[Server]>> connect success");
            System.out.println("[Channel "+ sid + "] A client has successfully connected, connection: " + getOnlineCount());
        } catch (IOException e) {
        	System.out.println("websocket IO Exception");
        }
    }

    /**
     * 連接關閉調用的方法
     */
    @OnClose
    public void onClose() {
        webSocketSet.remove(this);  //從set中刪除
        subOnlineCount();           //在線數減1
        //斷開連接情況下，更新主板佔用情況爲釋放
        System.out.println("[Channel "+ sid + "] A client has disconnected, connection: " + getOnlineCount());
        //這裏寫你 釋放的時候，要處理的業務
    }

    /**
     * 收到客戶端消息後調用的方法
     * @ Param message 客戶端發送過來的消息
     */
    @OnMessage
    public void onMessage(String message, Session session) {
        System.out.println("[Channel " + sid + "] " + message);
        //羣發消息
        for (WebSocketServer item : webSocketSet) {
            try {
                item.sendMessage(message);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    /**
     * @ Param session
     * @ Param error
     */
    @OnError
    public void onError(Session session, Throwable error) {
    	System.out.println("發生錯誤");
        error.printStackTrace();
    }

    /**
     * 實現服務器主動推送
     */
    public void sendMessage(String message) throws IOException {
        this.session.getBasicRemote().sendText(message);
    }

    /**
     * 羣發自定義消息
     */
    public static void sendInfo(String message, @PathParam("sid") String sid) throws IOException {
        System.out.println("推送消息到窗口" + sid + "，推送內容:" + message);

        for (WebSocketServer item : webSocketSet) {
            try {
                //這裏可以設定只推送給這個sid的，爲null則全部推送
                if (sid == null) {
//                    item.sendMessage(message);
                } else if (item.sid.equals(sid)) {
                    item.sendMessage(message);
                }
            } catch (IOException e) {
                continue;
            }
        }
    }

    public static synchronized int getOnlineCount() {
        return onlineCount;
    }

    public static synchronized void addOnlineCount() {
        WebSocketServer.onlineCount++;
    }

    public static synchronized void subOnlineCount() {
        WebSocketServer.onlineCount--;
    }

    public static CopyOnWriteArraySet<WebSocketServer> getWebSocketSet() {
        return webSocketSet;
    }
}
