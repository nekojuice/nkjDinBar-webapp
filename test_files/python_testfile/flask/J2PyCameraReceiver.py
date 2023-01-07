import cv2
import imagezmq
import zmq
import sys
from flask import Flask, render_template, Response
from flask_socketio import SocketIO


app = Flask(__name__)
socketio = SocketIO(app)

def Stream_receiver():
    receiver = imagezmq.ImageHub()
    while True:  # show streamed images until Ctrl-C
        rpi_name, image = receiver.recv_image()
        cv2.imshow(rpi_name, cv2.flip(image, 1)) # 1 window for each RPi
        key = cv2.waitKey(1) & 0xFF
        receiver.send_reply(b'OK')
        
        if key == ord("q"):
            Stream_trigger_client()
            #break

def Stream_trigger_client():
    while True:
        context = zmq.Context()
        trigger = context.socket(zmq.REQ)
        #trigger.connect("tcp://192.168.137.10:5556")
        trigger.connect("tcp://localhost:5556")
        
        trigger.send(b"END streaming")
        
        message = trigger.recv()
        print(message)
        sys.exit()
        #break

def Client2J():
    while True:
        context = zmq.Context()
        trigger = context.socket(zmq.REQ)
        trigger.connect("tcp://localhost:5557")
        
        trigger.send(b"END streaming")
        
        message = trigger.recv()
        print(message)

        #break

def Server2J():
    while True:
        context = zmq.Context()
        trigger = context.socket(zmq.REP)
        trigger.bind("tcp://*:5558")
            
        message = trigger.recv()
        print(message)
            
        trigger.send(b"got trigger")

@socketio.on('connectionTest')
def connectionTest(message):
    print('[Ja]->[Py]: ' + message)
    socketio.emit('connectionTest', 'cathihihi')  # 回傳訊息


### 啟動------------------------------------------------------
# 直接執行此py檔案才啟動

app.run(host='0.0.0.0',port='5000')


### 啟動------------------------------------------------------