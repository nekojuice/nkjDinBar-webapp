import RPi.GPIO as GPIO
import time


HORZ_PINS = [17,18,27,22]   # 設定水平轉軸腳位
VERT_PINS = [5,6,13,19]     # 設定垂直轉軸腳位
WAIT = 10                   # 延遲 ms

def Run1(STEPPER_PINS, wait_time=WAIT/float(1000)):
    GPIO.setmode(GPIO.BCM)
    for pin in STEPPER_PINS:
        GPIO.setup(pin, GPIO.OUT)   # 設定輸出腳位
        GPIO.output(pin, GPIO.LOW)  # 設定腳位初始是低電位0 高電位1   
    try:
        #-----------------
        GPIO.output(17, 1)
        GPIO.output(18, 0)
        GPIO.output(27, 0)
        GPIO.output(22, 0)
        time.sleep(wait_time) 
        #-----------------
        GPIO.output(17, 1)
        GPIO.output(18, 1)
        GPIO.output(27, 0)
        GPIO.output(22, 0)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 0)
        GPIO.output(18, 1)
        GPIO.output(27, 0)
        GPIO.output(22, 0)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 0)
        GPIO.output(18, 1)
        GPIO.output(27, 1)
        GPIO.output(22, 0)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 0)
        GPIO.output(18, 0)
        GPIO.output(27, 1)
        GPIO.output(22, 0)
        time.sleep(wait_time)
        #-----------------
    except KeyboardInterrupt:
        print('關閉程式')
    finally:
        GPIO.cleanup()
        
def Run2(STEPPER_PINS, wait_time=WAIT/float(1000)):
    GPIO.setmode(GPIO.BCM)
    for pin in STEPPER_PINS:
        GPIO.setup(pin, GPIO.OUT)   # 設定輸出腳位
        GPIO.output(pin, GPIO.LOW)  # 設定腳位初始是低電位0 高電位1   
    try:
        #-----------------
        GPIO.output(17, 0)
        GPIO.output(18, 0)
        GPIO.output(27, 1)
        GPIO.output(22, 0)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 0)
        GPIO.output(18, 0)
        GPIO.output(27, 1)
        GPIO.output(22, 1)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 0)
        GPIO.output(18, 0)
        GPIO.output(27, 0)
        GPIO.output(22, 1)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 1)
        GPIO.output(18, 0)
        GPIO.output(27, 0)
        GPIO.output(22, 1)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 1)
        GPIO.output(18, 0)
        GPIO.output(27, 0)
        GPIO.output(22, 0)
        time.sleep(wait_time)
        #-----------------
    except KeyboardInterrupt:
        print('關閉程式')
    finally:
        GPIO.cleanup()

def Runinv1(STEPPER_PINS, wait_time=WAIT/float(1000)):
    GPIO.setmode(GPIO.BCM)
    for pin in STEPPER_PINS:
        GPIO.setup(pin, GPIO.OUT)   # 設定輸出腳位
        GPIO.output(pin, GPIO.LOW)  # 設定腳位初始是低電位0 高電位1   
    try:
        #-----------------
        GPIO.output(17, 0)
        GPIO.output(18, 0)
        GPIO.output(27, 1)
        GPIO.output(22, 0)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 0)
        GPIO.output(18, 1)
        GPIO.output(27, 1)
        GPIO.output(22, 0)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 0)
        GPIO.output(18, 1)
        GPIO.output(27, 0)
        GPIO.output(22, 0)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 1)
        GPIO.output(18, 1)
        GPIO.output(27, 0)
        GPIO.output(22, 0)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 1)
        GPIO.output(18, 0)
        GPIO.output(27, 0)
        GPIO.output(22, 0)
        time.sleep(wait_time)
        #-----------------
    except KeyboardInterrupt:
        print('關閉程式')
    finally:
        GPIO.cleanup()
        
def Runinv2(STEPPER_PINS, wait_time=WAIT/float(1000)):
    GPIO.setmode(GPIO.BCM)
    for pin in STEPPER_PINS:
        GPIO.setup(pin, GPIO.OUT)   # 設定輸出腳位
        GPIO.output(pin, GPIO.LOW)  # 設定腳位初始是低電位0 高電位1   
    try:
        #-----------------
        GPIO.output(17, 1)
        GPIO.output(18, 0)
        GPIO.output(27, 0)
        GPIO.output(22, 0)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 1)
        GPIO.output(18, 0)
        GPIO.output(27, 0)
        GPIO.output(22, 1)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 0)
        GPIO.output(18, 0)
        GPIO.output(27, 0)
        GPIO.output(22, 1)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 0)
        GPIO.output(18, 0)
        GPIO.output(27, 1)
        GPIO.output(22, 1)
        time.sleep(wait_time)
        #-----------------
        GPIO.output(17, 0)
        GPIO.output(18, 0)
        GPIO.output(27, 1)
        GPIO.output(22, 0)
        time.sleep(wait_time)
        #-----------------
    except KeyboardInterrupt:
        print('關閉程式')
    finally:
        GPIO.cleanup()        