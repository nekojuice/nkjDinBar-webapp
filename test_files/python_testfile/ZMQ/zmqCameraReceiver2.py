# run this program on the Mac to display image streams from multiple RPis
import cv2
import imagezmq
import zmq
import sys


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


    
Stream_receiver()