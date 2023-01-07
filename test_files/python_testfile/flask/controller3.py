from flask import Flask, render_template, Response
from imutils.video import VideoStream
import cv2
from flask_socketio import SocketIO
import time
import threading
import os
import sys
# import RPi.GPIO as GPIO


app = Flask(__name__)
#camera = cv2.VideoCapture(0)
camera = cv2.VideoCapture(0, apiPreference=cv2.CAP_V4L)

# 控制相機(視訊串流)
def gen_frames():
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except KeyboardInterrupt:
        print('關閉相機')
        camera.stop()


### 網路------------------------------------------------------
# 視訊串流路徑
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
# 主頁面
@app.route('/')
def index():
    return render_template('controller.html')
### 網路------------------------------------------------------


### 馬達控制------------------------------------------------------
step_current = [0, 0]       # 記錄目前刻度(座標), [水平, 垂直], 初始值為0
step_target = [0, 0]        # 操控目標刻度, 如果busy=0 and target != current則Run
step_busy = [0, 0]          # Run時為1, 避免目前動作被干擾
STEP_MAX = (864, 512)       # 設定轉軸上限, 1024刻代表±90度
HORZ_PINS = [17,18,27,22]   # 設定水平轉軸腳位
VERT_PINS = [5,6,13,19]     # 設定垂直轉軸腳位
WAIT = 5                    # 設定馬達運作後暫停時間(速度)

SEQUENCE = [[1,0,0,0],  # 八步模式
            [1,1,0,0],
            [0,1,0,0],
            [0,1,1,0],
            [0,0,1,0],
            [0,0,1,1],
            [0,0,0,1],
            [1,0,0,1]]
SEQUENCE_LEN = len(SEQUENCE)    # 訊號序列長度=8

def Run(step_input, STEPPER_PINS, wait_time=WAIT/float(1000)): #輸入: 要移動的 (x, y)刻, []腳位, ms速度
    step_input = int(step_input)    # 防呆
    PINS_LEN = len(STEPPER_PINS)    # 腳位數=4
    
    print(STEPPER_PINS)
    # for pin in STEPPER_PINS:
    #     GPIO.setup(pin, GPIO.OUT)   # 設定輸出腳位
    #     GPIO.output(pin, GPIO.LOW)  # 設定腳位初始是低電位0 高電位1
    
    sequence_index = 0  # 記錄目前序列位置
    steps = 0           # 計步器
    direction = 0       # 方向1=順時針, -1=逆時針
    if step_input > 0: direction = 1
    elif step_input < 0: direction = -1
    else: direction = 0 # 假如你亂打, 方向設為0
    
    global step_busy
    if STEPPER_PINS == HORZ_PINS:   # 忙碌鎖, 工作中時設為1, 結束設為0
        step_busy[0] = 1
    if STEPPER_PINS == VERT_PINS:
        step_busy[1] = 1
        direction = -direction      # y軸因我們的設計相反...
        step_input = -step_input
    
    try:
        print('開始程式')
        while True:
            if steps == step_input:
                break
            # for pin in range(PINS_LEN): # 給0~3號位置pin 對應的SEQUENCE電位, eg. GPIO.output(17, 1)
            # #     #GPIO.output(STEPPER_PINS[pin], SEQUENCE[sequence_index][pin])
            #     print(STEPPER_PINS[pin], SEQUENCE[sequence_index][pin])
            # print('-'*10)
    
            steps += direction              # 操作後, 計步器靠近目標
            sequence_index += direction     # 操作後, 序列移動
            sequence_index %= SEQUENCE_LEN  # 取餘數讓序列在範圍(0~7)內移動
            time.sleep(wait_time)           # 暫停幾ms(速度)
    except KeyboardInterrupt:
        print('關閉程式')
    finally:
        if STEPPER_PINS == HORZ_PINS:   # 忙碌鎖, 結束設為0
            step_busy[0] = 0
            step_current[0] += step_input
            socketio.emit('horz_current', step_current[0])
        if STEPPER_PINS == VERT_PINS:
            step_busy[1] = 0
            step_current[1] -= step_input   # y軸相反, 但座標要是正的, 所以再-一次
            socketio.emit('vert_current', step_current[1])
        #GPIO.cleanup()
        print('結束!, 目前座標: ' + str(step_current) + '; 目標座標: ' + str(step_target) + '; 忙碌中: ' + str(step_busy))
        if step_current != step_target: # 如果未達到目標, 則自動執行
            execute()
### 馬達控制------------------------------------------------------


### socket------------------------------------------------------
socketio = SocketIO(app)

def max_filter(horz_input, vert_input):    # 最大值鎖定, 放入最終座標(step_target)
    global step_current
    global step_target
    step_target = [horz_input, vert_input]
    if step_target[0] != step_current[0]:    # 如果最終 != 目前
        if step_target[0] > STEP_MAX[0]:    # 如果目標爆表
            step_target[0] = STEP_MAX[0]
        elif step_target[0] < -STEP_MAX[0]:
            step_target[0] = -STEP_MAX[0]
    if step_target[1] != step_current[1]:    # 如果最終 != 目前
        if step_target[1] > STEP_MAX[1]:    # 如果目標爆表
            step_target[1] = STEP_MAX[1]
        elif step_target[1] < -STEP_MAX[1]:
            step_target[1] = -STEP_MAX[1]

def execute():
    step_change = [step_target[0] - step_current[0], step_target[1] - step_current[1]]
    if step_change[0] != 0 and step_busy[0] == 0:  # 如果改變量不是0 且非忙碌中, 則執行Run
        threading.Thread(target = Run, args = (step_change[0], HORZ_PINS)).start()
    if step_change[1] != 0 and step_busy[1] == 0:
        threading.Thread(target = Run, args = (step_change[1], VERT_PINS)).start()
    print('執行!, 目前座標: ' + str(step_current) + '; 目標座標: ' + str(step_target) + '; 改變量: ' + str(step_change) + '; 忙碌中: ' + str(step_busy))


@socketio.on('button_execute')   # web按鈕操控, 每次點擊輸入5刻 (輸入: 增加[x, y]刻)
def button_execute(horz_input, vert_input):
    step_change = [step_target[0] + horz_input, step_target[1] + vert_input]
    max_filter(*step_change)
    execute()

@socketio.on('coordinate_execute')     # web直接傳入目標 (輸入: 到[x, y]最終刻度)
def coordinate_execute(horz_input, vert_input):
    max_filter(int(horz_input), int(vert_input))
    execute()
    
@socketio.on('zero_point_execute')  # 歸零, 將記錄的step_current轉為負值並執行
def zero_point():
    coordinate_execute(0, 0)
    print('正在進行歸零...')
    
@socketio.on('update_step_reqiure') # 重整網頁時抓取現在座標
def update_step():
    socketio.emit('update_step_response', step_current)

@socketio.on('calibration')         # 校正, 將step_current設為0
def calibration():
    global step_current
    step_current = [0, 0]
    socketio.emit('update_step_response', step_current)

# @socketio.on('sys_restart')         # 重新啟動程式, 沒有套用
# def sys_restart():
#     zero_point()
#     time.sleep(5)
#     os.execl(sys.executable, os.path.abspath(__file__), *sys.argv) 
@socketio.on('sys_shutdown')        # 正常關閉程式, 含回到原點
def sys_shutdown():
    zero_point()
    threading.Thread(target = sys_shutdown_wait).start()    # 我不知道怎麼join, 所以把它獨立sleep5秒...

def sys_shutdown_wait():
    try:
        print('5秒後關閉程式!')
        time.sleep(5)
        os._exit(0)
    except:
        print('die')
### socket------------------------------------------------------


### 啟動------------------------------------------------------
# 直接執行此py檔案才啟動
if __name__ == '__main__':
    app.run(host='0.0.0.0')
### 啟動------------------------------------------------------