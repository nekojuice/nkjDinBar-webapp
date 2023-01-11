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
frame2path = './deepface_image/'

stream_receiver_stop_flag = True
ai1_stop_flag = True
ai2_stop_flag = True
ai3_stop_flag = True

rec_video_stopflag = True

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
def on_message(obj, msg):           # 接收自訂指令(訊息)
    if msg == "/fl hi":             # 測試
        ws.send("[flask]>> hello, connection to python Flask webapp is OK!")
    if msg == "/camera on":         # 相機
        thread_stream_receiver()
    if msg == "/camera off":
        stream_receiver_stop()
    if msg == "/mic on":            # flask端收音
        thread_mic_recv()
    if msg == "/mic off":
        mic_recv_stop() 
    if msg == "/rec v on":          # 錄製視訊
        thread_rec_video()
    if msg == "/rec v off":
        rec_video_stop()
    if msg == "/rec a on":          # 錄製音訊
        thread_rec_audio()
    if msg == "/rec a off":
        rec_audio_stop()
        
    if msg == "/snapshot":          # 拍照
        snapshot()
        
    if msg == "/fl exit":           # 關閉flask端
        ws.send("[flask]>> terminating process...")
        os._exit(0)
        
    if msg == "/ai1 on":            # ai模式
        ws.send("[flask]>> 執行ai1: 臉部追蹤-慢速")
        thread_ai1()
    if msg == "/ai1 off":
        ws.send("[flask]>> ai1: 結束")
        ai1_stop()
    if msg == "/ai2 on":
        ws.send("[flask]>> 執行ai2: 臉部追蹤-快速")
        thread_ai2()
    if msg == "/ai2 off":
        ws.send("[flask]>> ai2: 結束")
        ai2_stop()
    if msg == "/ai3 on":
        ws.send("[flask]>> 執行ai3: KCF人像選擇追蹤")
        thread_ai3()
    if msg == "/ai3 off":
        stop_ai3()
        ws.send("[flask]>> ai3: 結束")
        os.remove(frame2path+'0.jpg')
        stop_verify()
        ws.send('/rect cl')
        ws.send('/rect cl')
    if re.match('/ai3 t', msg):         # ai3專屬 選擇幾號目標
        _ = list(map(int, re.split(' ', msg)[-1:]))[0]
        print(_)
        ai3.tracking_selector(image, int(_))
        thread_verify()
    if msg == "/fl checkstatus":
        ws.send(f'/status camera {stream_receiver_stop_flag}')
        time.sleep(0.1)
        ws.send(f'/status mic {mic.stopflag}')
        time.sleep(0.1)
        ws.send(f'/status ai1 {ai1_stop_flag}')
        time.sleep(0.1)
        ws.send(f'/status ai2 {ai2_stop_flag}')
        time.sleep(0.1)
        ws.send(f'/status ai3 {ai3_stop_flag}')
        time.sleep(0.1)
        ws.send(f'/status rec_video {rec_video_stopflag}')
        time.sleep(0.1)
        ws.send(f'/status rec_audio {mic.rec_stopflag}')
        
        
# 影像串流 資料接收器
def thread_stream_receiver():
    threading.Thread(target = stream_receiver).start()
def stream_receiver():
    global stream_receiver_stop_flag
    stream_receiver_stop_flag = False
    try:
        while not stream_receiver_stop_flag:
            global image
            rpi_name, image = image_hub.recv_image()
            cv2.waitKey(1)
            image_hub.send_reply(b'OK')
    except:
        print('串流接收異常')
def stream_receiver_stop():
    global stream_receiver_stop_flag
    stream_receiver_stop_flag = True

# 影像串流 生成m-jpg
def gen_frames():
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
        print('一時影像生成失敗: 可能相機未開、延遲或通信障礙')

# 錄影存檔
def thread_rec_video():
    threading.Thread(target = rec_video).start()
def rec_video():
    global rec_video_stopflag
    rec_video_stopflag = False
    timeString = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(f"./record/save_video/{timeString}.avi", fourcc, 20.0, (640,  480))
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
    save_path = "./record/snapshot_image"  # 資料夾要先建好
    p = os.path.sep.join([save_path, f"{timeString}_{str(idx)}.png"])
    cv2.imwrite(p, image)
    idx += 1
    total += 1
    print(f'{total} pictures saved...')

# 音訊串流 python端即時撥放 (網頁上沒有聲音)
def thread_mic_recv():
    threading.Thread(target = mic_recv).start()
def mic_recv():
    try:
        mic.audio_receive()
    except:
        print('音訊串流發生例外而結束')
def mic_recv_stop():
    mic.stopflag = True
    
# 音訊存檔 python播放 錄音 結束後存檔
def thread_rec_audio():
    threading.Thread(target = rec_audio).start()
def rec_audio():
    try:
        mic.audio_record()
    except:
        print('音訊串流發生例外而結束')
def rec_audio_stop():
    mic.stopflag = True
    
# ai1 mediapipe 抓取人臉 單步模式
def thread_ai1():
    threading.Thread(target = run_ai1, args=(1000,)).start()
def run_ai1(scanrate):
    global ai1_stop_flag
    ai1_stop_flag = False
    try:
        while not ai1_stop_flag:
            try:
                rect_start_point, rect_end_point =  ai1.M_face(image)
                goCenter1(rect_start_point, rect_end_point, 250)
            except:
                pass
            finally:
                time.sleep(1/scanrate)
    except:
        print("ai1圖像辨識例外發生")
def ai1_stop():
    global ai1_stop_flag
    ai1_stop_flag = True
def goCenter1(start, end, bond):     # 檢測內框(人臉框) 是否超出外框(邊界框,bond:邊界大小)
    if start[0] < 320-(bond/2):
        ws.send("/pi a -8 0")
    if end[0] > 320+(bond/2):
        ws.send("/pi a 8 0")
    if start[1] < 240-(bond/2):
        ws.send("/pi a 0 -8")
    if end[1] > 240+(bond/2):
        ws.send("/pi a 0 8")

# ai2 mediapipe 抓取人臉 大步模式
def thread_ai2():
    threading.Thread(target = run_ai2, args=(1,)).start()
def run_ai2(scanrate):
    global ai2_stop_flag
    ai2_stop_flag = False
    try:
        while not ai2_stop_flag:
            try:
                rect_start_point, rect_end_point =  ai1.M_face(image)
                center = [(rect_start_point[0] + rect_end_point[0])/2, (rect_start_point[1] + rect_end_point[1])/2]
                goCenter2(center, 40)
            except:
                pass
            finally:
                time.sleep(1/scanrate)
    except:
        print("ai2圖像辨識例外發生")
def ai2_stop():
    global ai2_stop_flag
    ai2_stop_flag = True
def goCenter2(center, bond):    # center=人臉框中心座標, 檢測是否超出正中間bond大小的框
    move_step = [8*int(center[0]//8)-320, 8*int(center[1]//8)-240]
    if abs(move_step[0]) > bond or abs(move_step[1]) > bond:
        print(move_step)
        ws.send("/pi a " + str(move_step[0]) + " " + str(move_step[1]))

# ai3
def thread_ai3():
    threading.Thread(target=run_ai3, daemon=True, args=()).start()
def run_ai3():
    global ai3_stop_flag
    ai3_stop_flag = False
    while not ai3_stop_flag:
        try:
            coordinate = ai3.ai3(image)
            ws.send('/rect cl')
            ws.send('/rect cl')
            for i in range(len(coordinate)):
                ws.send(f'/rect {coordinate[i][0]} {coordinate[i][1]} {coordinate[i][2]} {coordinate[i][3]} {coordinate[i][4]}')
                ws.send(f'/rect {coordinate[i][0]} {coordinate[i][1]} {coordinate[i][2]} {coordinate[i][3]} {coordinate[i][4]}')
            if coordinate[0][0] == 'target':
                goCenter3(((coordinate[0][1] + (coordinate[0][3])/2),(coordinate[0][2] + (coordinate[0][4])/2)),40)
        except:
            pass
        time.sleep(0.25)
        if ai3_stop_flag:
            break
def stop_ai3():
    global ai3_stop_flag
    ai3_stop_flag = True
    ai3.tracking = False
def goCenter3(center, bond):    # 檢測中心點是否超出框, 超出則朝那個方向走2刻(16 step)
    move_step = [8*int(center[0]//8)-320, 8*int(center[1]//8)-240]
    if abs(move_step[0]) > bond or abs(move_step[1]) > bond:
        print(move_step)
        x3 = 0
        y3 = 0
        if move_step[0] > 0:
            x3 = 16
        if move_step[0] < 0:
            x3 = -16
        if move_step[1] > 0:
            y3 = 16
        if move_step[1] < 0:
            y3 = -16 
        ws.send(f"/pi a {x3} {y3}")

def thread_verify():        # ai3專屬 進入deepface辨識模式
    threading.Thread(target=run_verify, daemon=True, args=()).start()
def run_verify():
    global ai3_verify_stop_flag
    ai3_verify_stop_flag = False
    while not ai3_verify_stop_flag:
        try:
            ai3.verify()
        except:
            pass
        time.sleep(1)
def stop_verify():
    global ai3_verify_stop_flag
    ai3_verify_stop_flag = True
    ai3.tracking = False
    

# websocket
def run_socket_app():
    global ws
    ws = WebSocketApp(ADDR,on_open=on_open,on_message=on_message,on_error=on_error,on_close=on_close,on_data=on_data)
    ws.run_forever()

# flask
def run_flask_app():
    app.run(host='0.0.0.0', port='5000')

# imagehub
def run_imagehub():
    global image_hub
    image_hub = imagezmq.ImageHub()

if __name__ == '__main__':
    threading.Thread(target = run_socket_app).start()   # websocket client
    threading.Thread(target = run_flask_app).start()    # flask server
    threading.Thread(target = run_imagehub).start()     # imagezmq server
