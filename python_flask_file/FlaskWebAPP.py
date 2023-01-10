from websocket import WebSocketApp
import cv2
import threading
import imagezmq
from flask import Flask, Response, render_template
import os
import time
from scipy.io.wavfile import write
import re

import fl_mic_recv as mic

import fl_Mediapipe_face_deceted as ai1
import fl_yolo_KCF_v3 as ai3


app = Flask(__name__)
ADDR = 'ws://127.0.0.1:8080/websocket/100'

image = []
frame2path = '../deepface_image/'
ai3_stop_flag = False

# 將jpg投到網址
@app.route('/blank')
def blank():
    return render_template('blank.html')

@app.route('/video')
def video():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/audio')
def playaudio():
    return Response(mic.audio_receive(),mimetype="audio/x-wav;codec=pcm")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template("405.html"), 405

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
    if msg == "/camera on":
        t_stream_receiver.start()
    if msg == "/mic on":
        thread_mic_recv()
    
    if msg == "/snapshot":
        snapshot()
        
    if msg == "/rec v on":
        thread_rec_video()
    if msg == "/rec v off":
        rec_video_stop()
    
    if msg == "/rec a on":
        thread_rec_audio()
    if msg == "/rec a off":
        rec_audio_stop()
        
    if msg == "/mic off":
        mic_recv_stop()
        
    if msg == "/fl exit":
        ws.send("[flask]>> terminating process...")
        os._exit(0)
        
    if msg == "/ai1 on":
        ws.send("[flask]>> processing pi_Mediapipe_face_deceted.py...")
        thread_ai1()
    if msg == "/ai1 off":
        ws.send("[flask]>> terminating process: ai1")
        ai1_stop()
    if msg == "/ai2 on":
        thread_ai2()
    if msg == "/ai2 off":
        ws.send("[flask]>> terminating process: ai2")
        ai2_stop()
        
    if msg == "/ai3 on":
        thread_ai3()
    if msg == "/ai3 off":
        stop_ai3()
        os.remove(frame2path+'0.jpg')
        stop_verify()
        ws.send('/rect cl')
        ws.send('/rect cl')
    if re.match('/ai3 t', msg):
        _ = list(map(int, re.split(' ', msg)[-1:]))[0]
        print(_)
        ai3.tracking_selector(image, int(_))
        thread_verify()
        

        
# 影像串流 資料接收器
def stream_receiver():
    image_hub = imagezmq.ImageHub()
    try:
        while True:
            global image
            #global image_timestamp
            rpi_name, image = image_hub.recv_image()
            #image_timestamp = time.time()
            #print(image_timestamp)
            # cv2.imshow(rpi_name, cv2.flip(image, 1)) # 1 window for each RPi
            cv2.waitKey(1)
            image_hub.send_reply(b'OK')
    except:
        print('串流接收異常')

# 影像串流 生成m-jpg
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

# 錄影存檔
def thread_rec_video():
    t_rec_video = threading.Thread(target = rec_video)
    t_rec_video.start()
def rec_video():
    global rec_video_stopflag
    rec_video_stopflag = False
    timeString = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(f"../../save_video/{timeString}.avi", fourcc, 20.0, (640,  480))
    while not rec_video_stopflag:
        out.write(image)
        if rec_video_stopflag:
            print("影像錄製中止")
            out.release()
            break
        time.sleep(0.04)

def rec_video_stop():
    global rec_video_stopflag
    rec_video_stopflag = True
    
# 拍照
idx = 0
total = 0
def snapshot():
    timeString = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    global idx
    global total
    save_path = "../../save_image"  # 資料夾要先建好
    p = os.path.sep.join([save_path, f"{timeString}_{str(idx)}.png"])
    cv2.imwrite(p, image)
    idx += 1
    total += 1
    print(f'{total} pictures saved...')

# 音訊串流 網頁即時撥放
def mic_recv():
    try:
        mic.audio_receive()
    except:
        print('音訊串流發生例外而結束')
def thread_mic_recv():
    t_run_mic_recv = threading.Thread(target = mic_recv)
    t_run_mic_recv.start()
def mic_recv_stop():
    mic.stopflag = True
    
# 音訊存檔 python播放 結束後存檔
def rec_audio():
    try:
        mic.audio_record()
    except:
        print('音訊串流發生例外而結束')
def thread_rec_audio():
    t_run_rec_audio = threading.Thread(target = rec_audio)
    t_run_rec_audio.start()
def rec_audio_stop():
    mic.stopflag = True
    
# ai1 mediapipe 抓取人臉 單步模式
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

# ai2 mediapipe 抓取人臉 大步模式
def thread_ai2():
    t_run_ai2 = threading.Thread(target = run_ai2, args=(1,))
    t_run_ai2.start()
def goCenter2(center, bond):
    move_step = [8*int(center[0]//8)-320, 8*int(center[1]//8)-240]
    if abs(move_step[0]) > bond or abs(move_step[1]) > bond:
        print(move_step)
        ws.send("/pi a " + str(move_step[0]) + " " + str(move_step[1]))
def run_ai2(scanrate):
    global ai2_stop_flag
    ai2_stop_flag = 0
    try:
        while True:
            try:
                rect_start_point, rect_end_point =  ai1.M_face(image)
                center = [(rect_start_point[0] + rect_end_point[0])/2, (rect_start_point[1] + rect_end_point[1])/2]
                goCenter2(center, 40)
            except:
                pass
            finally:
                time.sleep(1/scanrate)
                if ai2_stop_flag == 1:
                    break
    except:
        print("ai2圖像辨識例外發生")
def ai2_stop():
    global ai2_stop_flag
    ai2_stop_flag = 1

# ai3
def thread_ai3():
    global ai3_stop_flag
    ai3_stop_flag = False
    threading.Thread(target=run_ai3, daemon=True, args=()).start()
def run_ai3():
    print('ai3 防遮擋追蹤啟動!')
    while not ai3_stop_flag:
        try:
            coordinate = ai3.ai3(image)
            ws.send('/rect cl')
            ws.send('/rect cl')
            for i in range(len(coordinate)):
                ws.send(f'/rect {coordinate[i][0]} {coordinate[i][1]} {coordinate[i][2]} {coordinate[i][3]} {coordinate[i][4]}')
                ws.send(f'/rect {coordinate[i][0]} {coordinate[i][1]} {coordinate[i][2]} {coordinate[i][3]} {coordinate[i][4]}')
        except:
            pass
        time.sleep(0.03)
        if ai3_stop_flag:
            break
def stop_ai3():
    global ai3_stop_flag
    ai3_stop_flag = True
    ai3.tracking = False

def thread_verify():
    threading.Thread(target=run_verify, daemon=True, args=()).start()
def run_verify():
    global ai3_verify_stop_flag
    ai3_verify_stop_flag = False
    while not ai3_verify_stop_flag:
        ai3.verify(image)
        time.sleep(0.5)
        if ai3_verify_stop_flag:
            break
def stop_verify():
    global ai3_verify_stop_flag
    ai3_verify_stop_flag = True
    ai3.tracking = False
    


# websocket
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

# flask
def run_flask_app():
    app.run(host='0.0.0.0', port='5000')
    

if __name__ == '__main__':
    t1_run_socket_app = threading.Thread(target = run_socket_app)
    t1_run_socket_app.start()
    t2_run_flask_app = threading.Thread(target = run_flask_app)
    t2_run_flask_app.start()
    t_stream_receiver = threading.Thread(target = stream_receiver)
    t_stream_receiver.start()
