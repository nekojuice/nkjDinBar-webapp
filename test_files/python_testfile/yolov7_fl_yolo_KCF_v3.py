import cv2
import time
import threading
import numpy as np
import math
import torch
from glob import glob
from deepface import DeepFace
import os


# 接收攝影機串流影像，採用多執行緒的方式，降低緩衝區堆疊圖幀的問題。


# kalman filter tracker
track_stop_flag = False
tracking = False
tracker = cv2.TrackerCSRT_create()
Frame1 = []
Frame2 = []
status = False
state = True
counter = 0
start_time = time.time()
time_counter = 0
prev_time = 0
# yolov5及權重檔
# model = torch.hub.load('ultralytics/yolov5', 'custom',
#                        path='D:/Eclipse/Workspace/JavaEE/python_flask_file/yolo5model_exp3_best', force_reload=False)
model = torch.hub.load('../yolov7','custom',source='local', path_or_model='./yolov7.pt', force_reload=True)
path = './deepface_image/'


# deepface辨識, 發生遮擋或意外時啟動
# def verify_start(image):
#         print('deepface verify started!')
#         threading.Thread(target=verify, daemon=True, args=(image)).start()
def verify():
    # verify fail counter
    global counter
    global state
    
    if tracking:
        if not state:
            counter += 1
            print('失敗: ' + str(counter) + ' /10')
        else:
            counter = 0
        score = DeepFace.verify(
            Frame1, Frame2, model_name='Facenet',
            distance_metric='cosine',
            enforce_detection=False, detector_backend='mediapipe' #ssd
        )
        print(score)
        state = score['verified']
        # if score['threshold'] < 0.4:

        if counter == 10:
            verify_stop()
        # time.sleep(1)
        
def verify_stop():
    global tracking
    tracking = False
    os.remove(path+'0.jpg')
    print('deepface verify stop!')

# 接收追蹤編號
def tracking_selector(image, num):
    if not track_stop_flag:
        track(image, main[num])
        
# tracker追蹤啟動
def track(image, coordinate):
    tracker.init(image, coordinate)  # 相機的image
    global tracking
    tracking = True



# ai主程序
# def ai3_start(image):
#     global stop_flag
#     stop_flag = False
#     print('ai3 防遮擋追蹤啟動!')
#     threading.Thread(target=ai3, daemon=True, args=(image)).start()
# def ai3_stop():
#     global stop_flag
#     stop_flag = True

def _coordinates(x, y): # 座標過濾
    return math.floor(x), math.floor(y)
def arr_sort(a):    # 多重目標編號
    new_arr = np.sort(a)
    order = []
    for i in new_arr:
        ind = np.where(a == i)[0][0]
        order.append(ind)
    return order
def ai3(image):
    # while True:
        global start_time
        global time_counter
        time_counter += 1
        fps = time.time() - start_time
        cur_time = time.time()
        global prev_time
        
        # if fps != 0:
            # cv2.putText(image, f'FPS:{fps:.2f}', (100, 80), cv2.FONT_HERSHEY_SIMPLEX,
            #     1, (0, 0, 255), 1, cv2.LINE_AA)
        print(f'FPS:{1/(cur_time - prev_time)}')
        prev_time = cur_time
        if tracking:
            success, point = tracker.update(image)
            if success:
                p1 = _coordinates(point[0], point[1])       # track座標
                p2 = _coordinates(point[0] + point[2], point[1] + point[3])

                # cv2.rectangle(image, p1, p2, (0, 0, 255), 3)
                # cv2.putText(image, 'main', p1, cv2.FONT_HERSHEY_SIMPLEX,
                #             1, (0, 0, 255), 1, cv2.LINE_AA)
                
                

                # save 1 picture for our main character
                _image = image[point[1]:point[1] +
                               point[3], point[0]:point[0]+point[2]]
                global Frame1
                Frame1 = image[point[1]:point[1] +
                               point[3], point[0]:point[0]+point[2]]
                
                pic_list = glob(path + '*')

                if len(pic_list) < 1:
                    cv2.imwrite(path + str(len(pic_list)) + '.jpg', _image)

                # if len(pic_list) == 1 and Frame2 == []:
                global Frame2
                Frame2 = cv2.imread(pic_list[0], 1)
                # verify(image)
                    
                print('tracking: ', p1, p2) # 測試用顯示座標
                return [['target' , p1[0], p1[1], p2[0]-p1[0], p2[1]-p1[1]]]
        else:
            global main
            main = []
            yolo = model(image)
            df = yolo.pandas().xyxy[0]
            mask = df['name'].eq('person')
            mask = df['confidence'] > 0.6
            # print(df[mask])
            xmin = df[mask]['xmin'].values   # yolo座標
            ymin = df[mask]['ymin'].values
            xmax = df[mask]['xmax'].values
            ymax = df[mask]['ymax'].values
            
            
            
            order = arr_sort(xmin)
            #main = [int(x1), int(y1), int(abs(x1-x2)), int(abs(y1-y2))]

            temp_list = []
            for i in order:
                # cv2.rectangle(image, (int(xmin[i]), int(ymin[i])), (int(
                #     xmax[i]), int(ymax[i])), (0, 255, 0), 2)
                # cv2.putText(image, str(index), (int(xmin[i]), int(ymin[i])), cv2.FONT_HERSHEY_SIMPLEX,
                #             1, (255, 0, 0), 1, cv2.LINE_AA)
                main.append([int(xmin[i]), int(ymin[i]), int(
                    abs(xmin[i]-xmax[i])), int(abs(ymin[i]-ymax[i]))])
                
                print('yolo編號: ',i , int(xmin[i]), int(ymin[i]), int(xmax[i]), int(ymax[i])) # 測試用顯示座標
                temp_list.append([i , int(xmin[i]), int(ymin[i]), int(xmax[i])-int(xmin[i]), int(ymax[i])-int(ymin[i])])
                
            print(temp_list)
            return temp_list
        # cv2.imshow('Image', image)

        # if cv2.waitKey(1) == 27:  
        #     cv2.destroyAllWindows()
        #     verify_stop()
        #     break

        # if cv2.waitKey(1) & 0xFF == 48 and main:  # 等待接收追蹤的編號
        #     track(main[0])
        # if stop_flag:
        #     verify_stop()
            # break
