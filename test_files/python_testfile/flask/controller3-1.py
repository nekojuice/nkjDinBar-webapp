from flask import Flask, render_template, Response
from imutils.video import VideoStream
import cv2
from flask_socketio import SocketIO
import time
import RPi.GPIO as GPIO
import argparse
import os
import sys

app = Flask(__name__)

# -o為輸出路徑(必要)，-s為拍照編號從幾號開始(預設0)
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True,
    help="path to output directory")
ap.add_argument("-s", "--start", type=int, default=0,
    help="start number, default is 0")
args = vars(ap.parse_args())

# -o 的路徑不存在就告訴你然後關閉
if not os.path.isdir(args['output']):
    print(f'Output directory {args["output"]} does not exist, create first...')
    sys.exit(2)


#camera = cv2.VideoCapture(0)
camera = cv2.VideoCapture(0, apiPreference=cv2.CAP_V4L)

# 視訊串流控制相機
def gen_frames():
    idx = args['start']
    total = 0
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            key = cv2.waitKey(1) & 0xFF
            if key == ord("p"):
                p = os.path.sep.join([args["output"], f"{str(idx).zfill(5)}.png"])
                cv2.imwrite(p, frame)
                idx+=1
                total+=1
                print(f'{total} pictures saved...')
            elif key == ord("q"):
                break
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
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

socketio = SocketIO(app)

step_current = [0, 0]
step_max = (864, 512)
HORZ_PINS = [17,18,27,22]
VERT_PINS = [5,6,13,19]

### 馬達控制------------------------------------------------------
def angle(a):    # motor_horz 角度換算
    return round(float(a) / float(360), 2)
def angle(b):    # motor_vert 角度換算 
    return round(float(b) / float(360), 2)


def Direction(steps, STEPS_PER_REVOLUTION):
    if STEPS_PER_REVOLUTION > 0:
        return 1
    elif STEPS_PER_REVOLUTION < 0:
        return -1

def Run(step_angle, STEPPER_PINS, direction=1, wait_time=5/float(1000)):
    GPIO.setmode(GPIO.BCM)
    
    STEPS_PER_REVOLUTION = int(step_angle)
    SEQUENCE = [[1,0,0,0],
                [1,1,0,0],
                [0,1,0,0],
                [0,1,1,0],
                [0,0,1,0],
                [0,0,1,1],
                [0,0,0,1],
                [1,0,0,1]]
    
    for pin in STEPPER_PINS:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    
    SEQUENCE_COUNT = len(SEQUENCE)
    PINS_COUNT = len(STEPPER_PINS)
    
    sequence_index = 0 # 記錄目前進行到哪個步驟的變數
    steps = 0 # 記錄目前已移動步數
    
    try:
        print('開始程式')
        while True:
            if steps == STEPS_PER_REVOLUTION:
                break
            for pin in range(PINS_COUNT): # 給3(?)根pin低電位
                GPIO.output(STEPPER_PINS[pin], SEQUENCE[sequence_index][pin])
    
            steps += direction

            direction = Direction(steps, STEPS_PER_REVOLUTION)
    
            sequence_index += direction
            sequence_index %= SEQUENCE_COUNT

            time.sleep(wait_time)
    except KeyboardInterrupt:
        print('關閉程式')
    finally:
        GPIO.cleanup()

def Run_horz(step_angle, direction=1, wait_time=5/float(1000), STEPPER_PINS=[17,18,27,22]):
    GPIO.setmode(GPIO.BCM)
    
    STEPS_PER_REVOLUTION = int(step_angle)
    SEQUENCE = [[1,0,0,0],
                [1,1,0,0],
                [0,1,0,0],
                [0,1,1,0],
                [0,0,1,0],
                [0,0,1,1],
                [0,0,0,1],
                [1,0,0,1]]
    
    for pin in STEPPER_PINS:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    
    SEQUENCE_COUNT = len(SEQUENCE)
    PINS_COUNT = len(STEPPER_PINS)
    
    sequence_index = 0 # 記錄目前進行到哪個步驟的變數
    steps = 0 # 記錄目前已移動步數
    
    try:
        print('開始程式')
        while True:
            if steps == STEPS_PER_REVOLUTION:
                break
            for pin in range(PINS_COUNT): # 給3(?)根pin低電位
                GPIO.output(STEPPER_PINS[pin], SEQUENCE[sequence_index][pin])
    
            steps += direction

            direction = Direction(steps, STEPS_PER_REVOLUTION)
    
            sequence_index += direction
            sequence_index %= SEQUENCE_COUNT

            time.sleep(wait_time)
    except KeyboardInterrupt:
        print('關閉程式')
    finally:
        GPIO.cleanup()

def Run_vert(angle, direction=1, wait_time=5/float(1000), STEPPER_PINS=[5,6,13,19]):
    GPIO.setmode(GPIO.BCM)
    
    STEPS_PER_REVOLUTION = int(64 * 64 * angle)
    SEQUENCE = [[1,0,0,0],
                [1,1,0,0],
                [0,1,0,0],
                [0,1,1,0],
                [0,0,1,0],
                [0,0,1,1],
                [0,0,0,1],
                [1,0,0,1]]
    
    for pin in STEPPER_PINS:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
    
    SEQUENCE_COUNT = len(SEQUENCE)
    PINS_COUNT = len(STEPPER_PINS)
    
    sequence_index = 0 # 記錄目前進行到哪個步驟的變數
    steps = 0 # 記錄目前已移動步數
    
    try:
        print('開始程式')
        while True:
            if steps == STEPS_PER_REVOLUTION:
                break
            for pin in range(PINS_COUNT): # 給3(?)根pin低電位
                GPIO.output(STEPPER_PINS[pin], SEQUENCE[sequence_index][pin])
    
            steps += direction

            direction = Direction(steps, STEPS_PER_REVOLUTION)
    
            sequence_index += direction
            sequence_index %= SEQUENCE_COUNT

            time.sleep(wait_time)
    except KeyboardInterrupt:
        print('關閉程式')
    finally:
        GPIO.cleanup()

### 馬達控制------------------------------------------------------

### socket------------------------------------------------------

    
@socketio.on('motor_execute')
def motor_execute(horz_input, vert_input): # 輸入step座標改變量
    global step_current
    step_change1 = 0
    step_change2 = 0
    
    step_current = [ step_current[0] + horz_input, step_current[1] + vert_input ]
    if horz_input != 0:
        if step_current[0] > step_max[0]: 
            step_current[0] = step_max[0]
            step_change1 = step_max[0] - step_current[0]
            # print('水平角度改變量' + str(step_change1))
        elif step_current[0] < -step_max[0]: 
            step_current[0] = -step_max[0]
            step_change1 = step_max[0] - step_current[0]
            # print('水平角度改變量' + str(step_change1))     
        else:
            step_change1 = horz_input
    if vert_input !=0:
        if step_current[1] > step_max[1]: 
            step_current[1] = step_max[1]
            step_change2 = step_max[1] - step_current[1]
            #print('垂直角度改變量' + str(step_change2))
        elif step_current[1] < -step_max[1]: 
            step_current[1] = -step_max[1]
            step_change2 = step_max[1] - step_current[1]
            #print('垂直角度改變量' + str(step_change2))
        else:
            step_change2 = vert_input
    
    print('角度改變量' + str(step_change1) + ', ' + str(step_change2))
    print('目前座標: ' + str(step_current))
    Run(step_change1, HORZ_PINS)
    Run(step_change2, VERT_PINS)
        
@socketio.on('execute')
def execute(horz_input, vert_input): # 輸入絕對step座標
    horz_input = int(horz_input)
    vert_input = int(vert_input)
    global step_current
    if horz_input != 0:
        if -step_max[0] <= horz_input <= step_max[0]:
            step_change1 = horz_input - step_current[0]
            print("horz change: " + str(step_change1))
            Run(step_change1, HORZ_PINS)
            step_current[0] = horz_input
    if vert_input != 0:
        if -step_max[1] <= vert_input <= step_max[1]:
            step_change2 = vert_input - step_current[1]
            print("vert change: " + str(step_change2))
            Run(step_change2, VERT_PINS)
            step_current[1] = vert_input
    print('當前角度: ' + str(step_current))

@socketio.on('zero_point')
def zero_point():
    global step_current
    print('正在進行歸零...')
    print('改變前角度: ' + str(step_current))
    step_change1 = -step_current[0]
    step_change2 = -step_current[1]
    if step_change1 != 0:
        Run(step_change1, HORZ_PINS)
    if step_change2 != 0:
        Run(step_change2, VERT_PINS)
    step_current = [0,0]
    print('step_change: ' + str(step_change1) + ', ' + str(step_change2))
    print('當前角度: ' + str(step_current))
    
### socket------------------------------------------------------

### 啟動------------------------------------------------------
# 直接執行此py檔案才啟動
if __name__ == '__main__':
    app.run(host='0.0.0.0')
# cv2.destroyAllWindows()
# camera.stop()
### 啟動------------------------------------------------------