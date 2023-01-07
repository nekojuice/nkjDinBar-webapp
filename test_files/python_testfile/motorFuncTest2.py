from websocket import WebSocketApp
import cv2
import threading
import os
import socket
import time
from imutils.video import VideoStream
import imagezmq
import re
import PiMotorFunction as piM


# ADDR = ws://[ip]:[port]/[path...]/[sid(channel)]
#ADDR = 'ws://127.0.0.1:8080/websocket/100'
ADDR = 'ws://192.168.137.1:8080/websocket/100'
step_current = [0, 0]       # 記錄目前刻度(座標), [水平, 垂直], 初始值為0
step_target = [16, 0]        # 操控目標刻度, 如果busy=0 and target != current則Run
step_busy = [0, 0]          # Run時為1, 避免目前動作被干擾
STEP_MAX = (864, 512)       # 設定轉軸上限, 1024刻代表±90度
HORZ_PINS = [17,18,27,22]   # 設定水平轉軸腳位
VERT_PINS = [5,6,13,19]     # 設定垂直轉軸腳位
SEQUENCE = [[1,1,0,0],  # -7    0
            [0,1,0,0],  # -6    1
            [0,1,1,0],  # -5    2
            [0,0,1,0],  # -4    3
            [0,0,1,1],  # -3    4
            [0,0,0,1],  # -2    5
            [1,0,0,1],  # -1    6
            [1,0,0,0],  # 八步模式  7
            [1,1,0,0],  # 1     8
            [0,1,0,0],  # 2     9
            [0,1,1,0],  # 3     10
            [0,0,1,0],  # 4     11
            [0,0,1,1],  # 5     12
            [0,0,0,1],  # 6     13
            [1,0,0,1]]  # 7     14

print(step_current)
step_current[0] += piM.Run_a_step('x', piM.check_direction(step_current[0], step_target[0]), 100)[0]
print(step_current)
step_current[0] += piM.Run_a_step('x', piM.check_direction(step_current[0], step_target[0]), 100)[0]
print(step_current)

