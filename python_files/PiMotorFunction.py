import time
# import RPi.GPIO as GPIO
import threading

### 馬達控制------------------------------------------------------
def check_direction(current, target):
    dif = target - current
    if dif != 0:
        return 1 if dif > 0 else -1
    else:
        return 0

def Run_a_step(axis, direction, scanRate): #Hz, 每秒掃描幾次 最大1000
    '''
    STEPPER_PINS : 4 int list
        Put 4 pins in a list [a, b, c, d]
    direction: int
        -1 (backward) or 0(won't do anything) or 1(forward)
    scanRate: int
        Hz, max value <= 1000
    '''
    if direction != 0:
        if axis == 'x':
            STEPPER_PINS = [17,18,27,22]
        elif axis == 'y':
            STEPPER_PINS = [5,6,13,19]
        
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
        if axis == 'x':       # 執行完 更新目前座標
            return [8*direction, 0]
        elif axis == 'y':
            return [0, 8*direction]
    else:
        return [0, 0]

def max_filter(input, STEP_MAX):    # 最大值鎖定, 放入最終座標(step_target)
    step_target_temp = [0, 0]
    if (-STEP_MAX[0] <= input[0] <= STEP_MAX[0]):
        step_target_temp[0] = input[0]
    else:
        if input[0] < -STEP_MAX[0]: step_target_temp[0] = -STEP_MAX[0]
        elif STEP_MAX[0] < input[0]: step_target_temp[0] = STEP_MAX[0]
    if (-STEP_MAX[1] <= input[1] <= STEP_MAX[1]):
        step_target_temp[1] = input[1]
    else:
        if input[1] < -STEP_MAX[1]: step_target_temp[1] = -STEP_MAX[1]
        elif STEP_MAX[1] < input[1]: step_target_temp[1] = STEP_MAX[1]
    return step_target_temp