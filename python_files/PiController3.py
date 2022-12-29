from websocket import WebSocketApp
import cv2
import threading
import os
import socket
import time
from imutils.video import VideoStream
import imagezmq
import re
import PiMotorFunction as piM
import pyaudio
import select

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
    # 測試連線是否通
    if msg == "/pi hi":
        ws.send("[pi]>> hello, connection to pi is OK!")
    # 開關麥克風串流
    if msg == "/pi mic on":
        
        
        ws.send("[pi]>> raspberry mic switching on...")
    if msg == "/pi mic off":
        ws.send("/java mic off")

        ws.send("[pi]>> raspberry mic switch off")
    # 開關相機, 同時開關串流
    if msg == "/pi camera on":
        ws.send("/java stream on")
        ws.send("[pi]>> raspberry camera switching on...")
        start_Stream_sender()
    if msg == "/pi camera off":
        ws.send("/java stream off")
        camera.release()
        ws.send("[pi]>> raspberry camera switch off")
    # 遠端結束程序...如果有意外了話
    if msg == "/pi exit":
        ws.send("[pi]>> terminating process...")
        ws.close()
        os._exit(0)
    # 顯示current/target座標
    if msg == "/pi show":
        ws.send("[pi]>> current: " + str(step_current) + " || target: " + str(step_target))
    # 開啟/關閉自動追蹤
    if msg == "/pi auto on":
        ws.send("[pi]>> auto_run is on")
        auto_run()
    if msg == "/pi auto off":
        ws.send("[pi]>> auto_run is off")
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
        
### 自動移動鏡頭(current track target) ###
def autorun_stop():
    global stop_autorun_flag
    stop_autorun_flag = 1
    piM.GPIO.cleanup()
def auto_run():
    global stop_autorun_flag
    stop_autorun_flag = 0
    global t3
    t3 = threading.Thread(target = run_x)
    t3.start()
    global t4
    t4 = threading.Thread(target = run_y)
    t4.start()
def run_x():
    global stop_autorun_flag
    try:
        while True:
            step_current[0] += piM.Run_a_step('x', piM.check_direction(step_current[0], step_target[0]), 1000, SEQUENCE)[0]
            if stop_autorun_flag == 1:
                break
    except Exception as e: 
        print(e)
        print('run_x 發生錯誤')
def run_y():
    global stop_autorun_flag
    try:
        while True:
            step_current[1] += piM.Run_a_step('y', piM.check_direction(step_current[1], step_target[1]), 1000, SEQUENCE)[1]
            if stop_autorun_flag == 1:
                break
    except Exception as e: 
        print(e)
        print('run_y 發生錯誤')
### 自動追蹤 ###


### 音訊發送 ###
def audio_stop():
    global audio_stop_flag
    audio_stop_flag = 1
def start_audio_sender():
    try:
        ###### t3_Audio_sender = threading.Thread(target = audio_sender)
        ###### t3_Audio_sender.start()
        ws.send("/java mic on")
    except:
        pass

# def audio_sender():
#     try:
#         ######## piAudio.audio_send()
#     except:
#         pass

def audio_send():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 8000
    CHUNK = 2048

    audio = pyaudio.PyAudio()

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('', 9999))
    serversocket.listen(5)


    def callback(in_data, frame_count, time_info, status):
        for s in read_list[1:]:
            s.send(in_data)
        return (None, pyaudio.paContinue)


    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)
    # stream.start_stream()

    read_list = [serversocket]
    print("recording...")

    try:
        while True:
            readable, writable, errored = select.select(read_list, [], [])
            for s in readable:
                if s is serversocket:
                    (clientsocket, address) = serversocket.accept()
                    read_list.append(clientsocket)
                    print("Connection from", address)
                else:
                    data = s.recv(1024)
                    if not data:
                        read_list.remove(s)
    except KeyboardInterrupt:
        pass


    print("finished recording")

    serversocket.close()
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
### 音訊發送 ###


### 視訊發送 ###
def start_Stream_sender():
    try:
        camera.release()
    except:
        pass
    global t2_Stream_sender
    t2_Stream_sender = threading.Thread(target = Stream_sender)
    t2_Stream_sender.start()
    ws.send("/java stream on")
    
def Stream_sender():
    try:
        global camera
        camera = cv2.VideoCapture(0, apiPreference=cv2.CAP_V4L)
        #sender = imagezmq.ImageSender(connect_to='tcp://127.0.0.1:5555')
        sender = imagezmq.ImageSender(connect_to='tcp://192.168.137.1:5555')

        rpi_name = socket.gethostname() # send RPi hostname with each image
        #camera.start()
        #camera = VideoStream(usePiCamera=True).start()
        time.sleep(1.0)  # allow camera sensor to warm up
        while True:  # send images as stream until Ctrl-C
            success, image = camera.read()
            if not success:
                break
            else:
                #image = camera.read()
                sender.send_image(rpi_name, image)
    except:
        print("串流異常")
### 視訊發送 ###

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
    t1_socket_app = threading.Thread(target = socket_app)
    t1_socket_app.start()
