from websocket import WebSocketApp
import cv2
import threading
import os
import socket
import time
from imutils.video import VideoStream
import imagezmq
from flask import Flask


app = Flask(__name__)
ADDR = 'ws://127.0.0.1:8080/websocket/100'


@app.route('/video')
def Stream_receiver():
    receiver = imagezmq.ImageHub()
    try:
        while True:  # show streamed images until Ctrl-C
            rpi_name, image = receiver.recv_image()
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except KeyboardInterrupt:
        print('關閉相機')


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
        Stream_sender()
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')