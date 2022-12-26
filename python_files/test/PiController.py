from websocket import WebSocketApp

# ws://[ip]:[port]/[path...]/[sid(channel)]
ADDR = 'ws://127.0.0.1:8080/websocket/100'

def on_open(obj):
    print(obj, str("connecting..."))
def on_error(obj, err):
    print(obj ,str(" err "), err)
def on_close(obj, status, msg):
    print(obj, msg)
    print("連線中斷")
def on_data(obj, msg, data, isContinue):
    print(obj, msg)
def on_message(obj, msg):    # 接收訊息
    if msg == "/pi camera on":
        ws.send("[pi]>> raspberry camera switch on")
    if msg == "/pi camera off":
        ws.send("[pi]>> raspberry camera switch off")
    if msg == "/pi disconnect":
        ws.send("[pi]>> disconnecting...")
        ws.close()

def socket_app():
    global ws
    ws = WebSocketApp(
        ADDR,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_data=on_data)
    ws.run_forever()

# def socket_client():
#     global ws
#     ws = WebSocket()
#     ws.connect(ADDR, origin=ADDR)
    # ws.send("python say hi")
    # print(ws.recv())
    # ws.close()

if __name__ == '__main__':
    socket_app()
    
    
