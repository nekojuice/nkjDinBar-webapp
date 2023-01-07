# run this program on each RPi to send a labelled image stream
import socket
import time
from imutils.video import VideoStream
import imagezmq
import zmq
import threading
import sys
import cv2


stop_flag = False

def Stream_sender():
    #sender = imagezmq.ImageSender(connect_to='tcp://192.168.52.146:5555')    # pi
    sender = imagezmq.ImageSender(connect_to='tcp://localhost:5555')          # laptop
    
    rpi_name = socket.gethostname() # send RPi hostname with each image
    
    #camera = VideoStream(usePiCamera=True).start() # pi camera, old
    #camera = VideoStream(0, apiPreference=cv2.CAP_V4L).start() # pi camera, new
    camera = VideoStream(0).start() # laptop camera
    
    time.sleep(2.0)  # allow camera sensor to warm up
    
    while True:  # send images as stream until Ctrl-C
        image = camera.read()
        sender.send_image(rpi_name, image)
        
        global stop_flag
        if stop_flag == True:
            camera.stop()
            break
        
def Stream_trigger_server():
    while True:
        context = zmq.Context()
        trigger = context.socket(zmq.REP)
        trigger.bind("tcp://*:5556")
        
        message = trigger.recv()
        print(message)
        
        trigger.send(b"got trigger")

        if message == b'END streaming':
            trigger.send(b"pi camera is off")
            print("收到結束訊號")
            stop_flag = True
        break


# t1 = threading.Thread(target = Stream_trigger_server).start()

t2 = threading.Thread(target = Stream_sender)
t2.daemon = True
t2.start()

while True:
    context = zmq.Context()
    trigger = context.socket(zmq.REP)
    trigger.bind("tcp://*:5556")
        
    message = trigger.recv()
    print(message)
        
    trigger.send(b"got trigger")

    if message == b'END streaming':
        #trigger.send(b"pi camera is off")
        print("收到結束訊號")
        stop_flag = True