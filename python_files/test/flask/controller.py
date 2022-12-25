from flask import Flask, render_template, Response
from imutils.video import VideoStream
import cv2
from flask_socketio import SocketIO
import time
import RPi.GPIO as GPIO


app = Flask(__name__)
#camera = cv2.VideoCapture(0)
camera = cv2.VideoCapture(0, apiPreference=cv2.CAP_V4L)

# 視訊串流控制相機
def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
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

ang_horz_current = 0
ang_vert_current = 0

ang_horz_target = 0
ang_vert_target = 0

ang_horz_change = 0
ang_vert_change = 0

ang_horz_max = (-75, 75)  # 設定[最小值(左), 最大值(右)
ang_vert_max = (-45, 45)  # 設定最小值(下), 最大值(上)

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

def Run_horz(angle, direction=1, wait_time=5/float(1000), STEPPER_PINS=[17,18,27,22]):
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

def motor_horz(ang_horz_input):
    global ang_horz_current
    ang_horz_target = ang_horz_current + ang_horz_input
    if ang_horz_target > ang_horz_max[1]:
        ang_horz_target = ang_horz_max[1]   
    elif ang_horz_target < ang_horz_max[0]:
        ang_horz_target = ang_horz_max[0]
    ang_horz_change = ang_horz_input - ang_horz_current
    Run_horz(float(angle(ang_horz_change)))
    ang_horz_current = ang_horz_target

def motor_vert(ang_vert_input):
    global ang_vert_current
    ang_vert_target = ang_vert_current + ang_vert_input
    if ang_vert_target > ang_vert_max[1]:
        ang_vert_target = ang_vert_max[1]   
    elif ang_vert_target < ang_vert_max[0]:
        ang_vert_target = ang_vert_max[0]
    ang_vert_change = ang_vert_input - ang_vert_current
    Run_vert(float(angle(ang_vert_change)))
    ang_vert_current = ang_vert_target
    
@socketio.on('motor_execute')
def motor_execute(ang_horz_input, ang_vert_input):
    global ang_horz_current
    global ang_vert_current
    motor_horz(ang_horz_input)
    motor_vert(ang_vert_input)
    print(ang_horz_current, ang_vert_current)
### socket------------------------------------------------------

### 啟動------------------------------------------------------
# 直接執行此py檔案才啟動
if __name__ == '__main__':
    app.run(host='0.0.0.0')
# cv2.destroyAllWindows()
# camera.stop()
### 啟動------------------------------------------------------