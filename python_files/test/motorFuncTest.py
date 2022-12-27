import time
import threading

step_current = [0, 0]       # 記錄目前刻度(座標), [水平, 垂直], 初始值為0
step_target = [0, 0]        # 操控目標刻度, 如果busy=0 and target != current則Run
step_busy = [0, 0]          # Run時為1, 避免目前動作被干擾
STEP_MAX = (864, 512)       # 設定轉軸上限, 1024刻代表±90度
HORZ_PINS = [17,18,27,22]   # 設定水平轉軸腳位
VERT_PINS = [5,6,13,19]     # 設定垂直轉軸腳位
WAIT = 5                    # 設定馬達運作後暫停時間(速度)

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


def autoRun():
    check_direction(step_current[0], step_target[0])
    check_direction(step_current[1], step_target[1])

def check_direction(current, target):
    dif = target - current
    if dif != 0:
        return 1 if dif > 0 else -1
    else:
        return 0

def Run_a_step(STEPPER_PINS, direction, scanRate): #Hz, 每秒掃描幾次 最大1000
    '''
    STEPPER_PINS : 4 int list
        Put 4 pins in a list [a, b, c, d]
    direction: int
        -1 (backward) or 0(won't do anything) or 1(forward)
    scanRate: int
        Hz, max value <= 1000
    '''
    if direction != 0:
        PINS_LEN = len(STEPPER_PINS)
        # for pin in STEPPER_PINS:
        #     GPIO.setup(pin, GPIO.OUT)   # 設定輸出腳位
        #     GPIO.output(pin, GPIO.LOW)  # 設定腳位初始是低電位0 高電位1
        
        sequence_index = 7
        while 0 <= sequence_index <= 14:
            # for pin in range(PINS_LEN): # 給0~3號位置pin 對應的SEQUENCE電位, eg. GPIO.output(17, 1)
            #     GPIO.output(STEPPER_PINS[pin], SEQUENCE[sequence_index][pin])
            sequence_index += direction
            time.sleep((1/scanRate))
   
        
# Run_a_step(HORZ_PINS, 1, 100)
step_target = [2, -5]
print(check_direction(step_current[1], step_target[1]))