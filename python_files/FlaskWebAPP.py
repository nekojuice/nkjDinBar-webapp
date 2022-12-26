from websocket import WebSocketApp
import cv2
# import asyncio
import threading
from imutils.video import VideoStream
import imagezmq
from flask import Flask, Response


app = Flask(__name__)
ADDR = 'ws://127.0.0.1:8080/websocket/100'
# loop = asyncio.get_event_loop()


@app.route('/video')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    #receiver = imagezmq.ImageHub()
    try:
        while True:  # show streamed images until Ctrl-C
            #rpi_name, image = receiver.recv_image()
            ret, buffer = cv2.imencode('.jpg', image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except KeyboardInterrupt:
        print('關閉相機')

def Stream_receiver_origin():
    image_hub = imagezmq.ImageHub()
    try:
        while True:  # show streamed images until Ctrl-C
            global image
            rpi_name, image = image_hub.recv_image()
            cv2.imshow(rpi_name, cv2.flip(image, 1)) # 1 window for each RPi
            cv2.waitKey(1)
            image_hub.send_reply(b'OK')
    except:
        print('串流異常')


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
    if msg == "/flask hi":
        ws.send("[flask]>> hello, connection to python Flask webapp is OK!")
    if msg == "/pi camera on":
        t3_Stream_receiver_origin.start()


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



# async def asycn1(): 
#     await run_socket_app()
# async def asycn2(): 
#     await run_flask_app()

# tasks = [asyncio.ensure_future(asycn1()),
#          asyncio.ensure_future(asycn2())]


if __name__ == '__main__':
    t1_run_socket_app = threading.Thread(target = run_socket_app)
    t1_run_socket_app.start()
    t2_run_flask_app = threading.Thread(target = run_flask_app)
    t2_run_flask_app.start()
    t3_Stream_receiver_origin = threading.Thread(target = Stream_receiver_origin)
    t3_Stream_receiver_origin.start()
