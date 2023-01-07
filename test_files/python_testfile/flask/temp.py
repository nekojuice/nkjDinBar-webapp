from flask import Flask, render_template, Response
from imutils.video import VideoStream
import cv2
from flask_socketio import SocketIO
import time
import threading

step_current = [0, 0]       # 記錄目前刻度(座標), [水平, 垂直], 初始值為0
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
    step_input = int(step_input)
    PINS_LEN = len(STEPPER_PINS)    # 腳位數=4
    
    # for pin in STEPPER_PINS:
    #     GPIO.setup(pin, GPIO.OUT)   # 設定輸出腳位
    #     GPIO.output(pin, GPIO.LOW)  # 設定腳位初始是低電位0 高電位1
    
    sequence_index = 0  # 記錄目前序列位置
    steps = 0           # 計步器
    direction = 0       # 方向1=順時針, -1=逆時針
    if step_input > 0:
        direction = 1
    elif step_input < 0:
        direction = -1
    else: 
        direction = 0   # 假如你亂打, 方向設為0
    
    try:
        print('開始程式')
        while True:
            if steps == step_input:
                break
            for pin in range(PINS_LEN): # 給0~3號位置pin 對應的SEQUENCE電位, eg. GPIO.output(17, 1)
                # GPIO.output(STEPPER_PINS[pin], SEQUENCE[sequence_index][pin])
                print(STEPPER_PINS[pin], SEQUENCE[sequence_index][pin])
            print('-'*10)
    
            steps += direction              # 操作後, 計步器靠近目標
            sequence_index += direction     # 操作後, 序列移動
            sequence_index %= SEQUENCE_LEN  # 取餘數讓序列在範圍(0~7)內移動

            time.sleep(wait_time)           # 暫停幾ms(速度)
    except KeyboardInterrupt:
        print('關閉程式')
    # finally:
    #     GPIO.cleanup()


#Run(-2, HORZ_PINS)
#Run(3, VERT_PINS)
threading.Thread(target = Run, args = (-2, HORZ_PINS)).start()
threading.Thread(target = Run, args = (3, VERT_PINS)).start()
