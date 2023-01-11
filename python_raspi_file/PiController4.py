from websocket import WebSocketApp
import cv2
import threading
import os
import socket
import time
from imutils.video import VideoStream
import imagezmq
import re
import pyaudio
import select

import piMotorFunction2 as piM
import pi_mic_send as mic

stream_sender_stop_flag = True
autorun_stop_flag = True

# ADDR = ws://[ip]:[port]/[path...]/[sid(channel)]
#ADDR = 'ws://127.0.0.1:8080/websocket/100'
ADDR = 'ws://192.168.137.1:8080/websocket/100'
step_current = [0, 0]       # 記錄目前刻度(座標), [水平, 垂直], 初始值為0
step_target = [0, 0]        # 操控目標刻度, 如果busy=0 and target != current則Run
step_busy = [0, 0]          # Run時為1, 避免目前動作被干擾
STEP_MAX = (864, 512)       # 設定轉軸上限, 1024刻代表±90度
HORZ_PINS = [17,18,27,22]   # 設定水平轉軸腳位
VERT_PINS = [5,6,13,19]     # 設定垂直轉軸腳位
SEQUENCE = [[1,1,0,0],  # -7    0
            [0,1,0,0],  # -6    1
            [0,1,1,0],  # -5    2
            [0,0,1,0],  # -4    3
            [0,0,1,1],  # -3    4
            [0,0,0,1],  # -2    5
            [1,0,0,1],  # -1    6
            [1,0,0,0],  # 八步模式  7
            [1,1,0,0],  # 1     8
            [0,1,0,0],  # 2     9
            [0,1,1,0],  # 3     10
            [0,0,1,0],  # 4     11
            [0,0,1,1],  # 5     12
            [0,0,0,1],  # 6     13
            [1,0,0,1]]  # 7     14

def on_open(obj):
    print(obj, str("connecting..."))
def on_error(obj, err):
    print(obj ,str(" err "), err)
def on_close(obj, status, msg):
    print(obj, msg)
    print("連線中斷")
def on_data(obj, msg, data, isContinue):
    print(obj, msg)
def on_message(obj, msg):    # 接收訊息(自定義指令)
    global step_current
    global step_target
    if msg == "/fl checkstatus":
        ws.send(f'/status motor {autorun_stop_flag}')
    # 測試連線是否通
    if msg == "/pi hi":
        ws.send("[pi]>> hello, connection to pi is OK!")
    # 開關麥克風串流
    if msg == "/mic on":
        thread_mic_recv()
        ws.send("[pi]>> raspberry mic switching on...")
        #ws.send("/java audio on")  # 重整控制面板的iframe 因為buffer要30秒先停用
    if msg == "/mic off":
        ws.send("/java mic off")
        mic_send_stop()
        ws.send("[pi]>> raspberry mic switch off")
        #ws.send("/java audio off")
    # 音訊錄製 
    if msg == "/rec a on":
        thread_mic_recv()
        ws.send("[pi]>> raspberry mic switching on...")
    if msg == "/rec a off":
        ws.send("/java mic off")
        mic_send_stop()
        ws.send("[pi]>> raspberry mic switch off")
    
    # 開關相機, 同時開關串流
    if msg == "/camera on":
        ws.send("/java stream on")
        ws.send("[pi]>> raspberry camera switching on...")
        thread_stream_sender()
    if msg == "/camera off":
        ws.send("/java stream off")
        ws.send("[pi]>> raspberry camera switch off")
        stream_sender_stop()
    # 遠端結束程序...如果有意外了話
    if msg == "/pi exit":
        ws.send("[pi]>> terminating process...")
        ws.close()
        os._exit(0)
    # 顯示current/target座標
    if msg == "/pi show":
        ws.send("[pi]>> current: " + str(step_current) + " || target: " + str(step_target))
    # 開啟/關閉馬達
    if msg == "/m on":
        ws.send("[pi]>> auto_run is on")
        auto_run()
    if msg == "/m off":
        ws.send("[pi]>> auto_run is off")
        piM.motor_on_flag = False
        autorun_stop()
    # 設定target座標
    if re.match('/pi t', msg):
        step_target = (piM.max_filter(list(map(int, re.split(' ', msg)[-2:])), STEP_MAX))
        ws.send("[pi]>> current: " + str(step_current) + " || target: " + str(step_target))
    if re.match('/pi c', msg):
        step_current = (piM.max_filter(list(map(int, re.split(' ', msg)[-2:])), STEP_MAX))
        ws.send("[pi]>> current: " + str(step_current) + " || target: " + str(step_target))
    # 增加單步
    if re.match('/pi a', msg):
        _ = list(map(int, re.split(' ', msg)[-2:]))
        a = step_target[0] if _[0] == 0 else step_current[0] + _[0]
        b = step_target[1] if _[1] == 0 else step_current[1] + _[1]
        step_target = (piM.max_filter([a,b], STEP_MAX))
        
### 馬達開關 ###
def auto_run():
    global autorun_stop_flag
    autorun_stop_flag = False
    threading.Thread(target = run_x).start()
    threading.Thread(target = run_y).start()
def run_x():
    global autorun_stop_flag
    try:
        while not autorun_stop_flag:
            step_current[0] += piM.Run_a_step('x', piM.check_direction(step_current[0], step_target[0]), 500, SEQUENCE)[0]
    except Exception as e: 
        print(e)
        print('run_x 發生錯誤')
def run_y():
    global autorun_stop_flag
    try:
        while not autorun_stop_flag:
            step_current[1] += piM.Run_a_step('y', piM.check_direction(step_current[1], step_target[1]), 500, SEQUENCE)[1]
    except Exception as e: 
        print(e)
        print('run_y 發生錯誤')
def autorun_stop():
    global autorun_stop_flag
    autorun_stop_flag = True
    piM.GPIO.cleanup()

### 音訊發送 ###
def mic_send():
    mic.stopflag = False
    try:
        mic.audio_send()
    except:
        print('音訊串流發生例外而結束')
def thread_mic_recv():
    t_run_mic_send = threading.Thread(target = mic_send)
    t_run_mic_send.start()
def mic_send_stop():
    mic.stopflag = True


### 視訊發送 ###
def thread_stream_sender():
    threading.Thread(target = stream_sender).start()
def stream_sender():
    global stream_sender_stop_flag
    stream_sender_stop_flag = False
    try:
        global camera
        camera = cv2.VideoCapture(0, apiPreference=cv2.CAP_V4L)
        #sender = imagezmq.ImageSender(connect_to='tcp://127.0.0.1:5555')
        sender = imagezmq.ImageSender(connect_to='tcp://192.168.137.1:5555')

        rpi_name = socket.gethostname() # 設定raspi hostname
        time.sleep(1.0)
        while not stream_sender_stop_flag:
            success, image = camera.read()
            if not success:
                break
            else:
                sender.send_image(rpi_name, image)
        camera.release()    # 跳出迴圈後清除相機
    except:
        print("串流異常")
        camera.release()
def stream_sender_stop():
    global stream_sender_stop_flag
    stream_sender_stop_flag = True

# socket
def socket_app():
    global ws
    ws = WebSocketApp(ADDR,on_open=on_open,on_message=on_message,on_error=on_error,on_close=on_close,on_data=on_data)
    ws.run_forever()
    

if __name__ == '__main__':
    threading.Thread(target = socket_app).start()
