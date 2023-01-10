import cv2
import time
import threading
import numpy as np
import math
import torch
from glob import glob
from deepface import DeepFace

# 接收攝影機串流影像，採用多執行緒的方式，降低緩衝區堆疊圖幀的問題。
class ipcamCapture:
    def __init__(self, URL):
        self.Frame = []
        self.Frame2 = []
        self.status = False
        self.isstop = False
        # kalman filter tracker
        self.tracker = cv2.TrackerCSRT_create() 
        self.tracking = False

	# 攝影機連接。
        self.capture = cv2.VideoCapture(URL)

    def set_Frame2(self, Frame2):
        self.Frame2 = Frame2
    
    def start(self):
	# 把程式放進子執行緒，daemon=True 表示該執行緒會隨著主執行緒關閉而關閉。
        print('ipcam started!')
        threading.Thread(target=self.queryframe, daemon=True, args=()).start()
    
    def stop(self):
        self.isstop = True
        print('ipcam stopped!')
    
    def verify_start(self):
        print('verify started!')
        threading.Thread(target=self.verify, daemon=True, args=()).start()

    def verify_stop(self):
        self.tracking = False
        print('verify stop!')

    def getframe(self):
	# 當有需要影像時，再回傳最新的影像。
        return self.Frame.copy()
        
    def queryframe(self):
        while (not self.isstop):
            self.status, self.Frame = self.capture.read()
        
        self.capture.release()

    def verify(self):
        # verify fail counter
        counter = 0
        state = True
        while self.tracking:

            if not state:
                counter += 1
            else:
                counter = 0
                
            score = DeepFace.verify(
                self.Frame, self.Frame2, model_name='Facenet', 
                distance_metric='cosine', 
                enforce_detection=False, detector_backend='ssd'
                )
            print(score)
            state = score['verified']
            #if score['threshold'] < 0.4:
            
            if counter == 10:
                self.verify_stop()
            time.sleep(1)
        
    def track(self, coordinate):
        self.tracker.init(image, coordinate)
        self.tracking = True


def arr_sort(a):
    new_arr = np.sort(a)
    order = []
    for i in new_arr:
        ind = np.where(a == i)[0][0]
        order.append(ind)
    return order


def _coordinates(x, y):
    return math.floor(x), math.floor(y)


model = torch.hub.load('ultralytics/yolov5', 'custom',
    path='/Users/leo/Downloads/yolo_v5/yolov5/runs/train/exp3/weights/best.pt', force_reload=True)
path = '/Users/leo/git_workspace/Tools/images/'
cap = ipcamCapture(0)

cap.start()
time.sleep(1)

while True:
    image = cap.getframe()
    
    if cap.tracking:
        success, point = cap.tracker.update(image)
        if success:
            p1 = _coordinates(point[0], point[1])
            p2 = _coordinates(point[0] + point[2], point[1] + point[3])
                
            cv2.rectangle(image, p1, p2, (0, 0, 255), 3)
            cv2.putText(image, 'main', p1, cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 0, 255), 1, cv2.LINE_AA)
                
            # save 1 picture for our main character
            _image = image[point[1]:point[1]+point[3], point[0]:point[0]+point[2]]
            pic_list = glob(path + '*')
                    
            if len(pic_list) < 1:     
                cv2.imwrite(path + str(len(pic_list)) + '.jpg', _image)
            
            if len(pic_list) == 1 and cap.Frame2 == []:
                cap.set_Frame2(cv2.imread(pic_list[0], 1))
                cap.verify_start()
        
    else:
        main = []
        yolo = model(image)
        df = yolo.pandas().xyxy[0]
        mask = df['name'].eq('person')
        mask = df['confidence'] > 0.6
        #print(df[mask])
        xmin = df[mask]['xmin'].values
        ymin = df[mask]['ymin'].values
        xmax = df[mask]['xmax'].values
        ymax = df[mask]['ymax'].values
            
        order = arr_sort(xmin)
        #main = [int(x1), int(y1), int(abs(x1-x2)), int(abs(y1-y2))]

        for index, i in enumerate(order):
            cv2.rectangle(image, (int(xmin[i]), int(ymin[i])), (int(xmax[i]), int(ymax[i]) ), (0, 255, 0), 2)
            cv2.putText(image, str(index), (int(xmin[i]), int(ymin[i])), cv2.FONT_HERSHEY_SIMPLEX,
                1, (255, 0, 0), 1, cv2.LINE_AA)
            main.append([int(xmin[i]), int(ymin[i]), int(abs(xmin[i]-xmax[i])), int(abs(ymin[i]-ymax[i]))])
            
    cv2.imshow('Image', image)

    if cv2.waitKey(1) == 27:
        cv2.destroyAllWindows()
        cap.verify_stop()
        cap.stop()
        break

    if cv2.waitKey(1) & 0xFF == 48 and main:
        cap.track(main[0])