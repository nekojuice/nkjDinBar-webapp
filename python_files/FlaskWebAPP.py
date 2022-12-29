from websocket import WebSocketApp
import cv2
# import asyncio
import threading
from imutils.video import VideoStream
import imagezmq
from flask import Flask, Response, render_template
import os
import time

import Pi_mic_send as piAudio
import pi_Mediapipe_face_deceted as ai1


app = Flask(__name__)
ADDR = 'ws://127.0.0.1:8080/websocket/100'

# 串流資料接收器
def Stream_receiver():
    image_hub = imagezmq.ImageHub()
    try:
        while True:
            global image
            rpi_name, image = image_hub.recv_image()
            # cv2.imshow(rpi_name, cv2.flip(image, 1)) # 1 window for each RPi
            cv2.waitKey(1)
            image_hub.send_reply(b'OK')
    except:
        print('串流接收異常')

# 生成m-jpg
def gen_frames():   ## 這裡怪怪的
    time.sleep(1)
    try:
        while True:
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except KeyboardInterrupt:
        print('串流被管理員強制終止')
    except:
        print('串流生成失敗...可能相機未開或通信障礙')

# 將jpg投到網址
@app.route('/video')
def video():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/blank')
def blank():
    return render_template('blank.html')

def on_open(obj):
    print(obj, str("連線中..."))
def on_error(obj, err):
    print(obj ,str("連線錯誤發生"), err)
def on_close(obj, status, msg):
    print(obj, msg)
    print("連線中斷")
def on_data(obj, msg, data, isContinue):
    print(obj, msg)
def on_message(obj, msg):    # 接收自訂指令(訊息)
    if msg == "/fl hi":
        ws.send("[flask]>> hello, connection to python Flask webapp is OK!")
    if msg == "/pi camera on":
        t3_Stream_receiver.start()
    if msg == "/fl exit":
        ws.send("[flask]>> terminating process...")
        os._exit(0)
        
    if msg == "/fl ai1 on":
        ws.send("[flask]>> processing pi_Mediapipe_face_deceted.py...")
        thread_ai1()
    if msg == "/fl ai1 off":
        ws.send("[flask]>> terminating process: ai1")
        ai1_stop()


# ai1 mediapipe face rec.
def goCenter(start, end, bond):
    if start[0] < 320-(bond/2):
        ws.send("/pi a -8 0")
    if end[0] > 320+(bond/2):
        ws.send("/pi a 8 0")
    if start[1] < 240-(bond/2):
        ws.send("/pi a 0 -8")
    if end[1] > 240+(bond/2):
        ws.send("/pi a 0 8")
def thread_ai1():
    t4_run_ai1 = threading.Thread(target = run_ai1, args=(1000,))
    t4_run_ai1.start()
def run_ai1(scanrate):
    global ai1_stop_flag
    ai1_stop_flag = 0
    try:
        while True:
            try:
                rect_start_point, rect_end_point =  ai1.M_face(image)
                goCenter(rect_start_point, rect_end_point, 250)
            except:
                pass
            finally:
                time.sleep(1/scanrate)
                if ai1_stop_flag == 1:
                    break
    except:
        print("ai1圖像辨識例外發生")
def ai1_stop():
    global ai1_stop_flag
    ai1_stop_flag = 1
          
def run_socket_app():
    global ws
    ws = WebSocketApp(
        ADDR,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_data=on_data)
    ws.run_forever()

def run_flask_app():
    app.run(host='0.0.0.0', port='5000')
    

if __name__ == '__main__':
    t1_run_socket_app = threading.Thread(target = run_socket_app)
    t1_run_socket_app.start()
    t2_run_flask_app = threading.Thread(target = run_flask_app)
    t2_run_flask_app.start()
    t3_Stream_receiver = threading.Thread(target = Stream_receiver)
    t3_Stream_receiver.start()
