import cv2
import mediapipe as mp
import os
import torch

print(os.path.dirname(mp.__file__))

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_face_mesh = mp.solutions.face_mesh


def face_rec(face, w, h):
  x_top_left = int(face.landmark[54].x * w)
  y_top_left = int(face.landmark[54].y * h)

  x_top_right = int(face.landmark[284].x * w)
  y_top_right = int(face.landmark[284].y * h)
  
  x_bottom_left = int(face.landmark[150].x * w)
  y_bottom_left = int(face.landmark[150].y * h)

  x_bottom_right = int(face.landmark[379].x * w)
  y_bottom_right = int(face.landmark[379].y * h)
  return [x_top_left, y_top_left, x_top_right, y_top_right, x_bottom_left, y_bottom_left, x_bottom_right, y_bottom_right]


def distance(x1, y1, x2, y2):
  return (abs(x1 - x2) ** 2 + abs(y1 - y2) ** 2) ** 0.5  


# For webcam input:
def webcam_input():
  drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
  cap = cv2.VideoCapture(0)
  model = torch.hub.load('ultralytics/yolov5', 'custom',
                       path='/Users/leo/Downloads/yolo_v5/yolov5/runs/train/exp3/weights/best.pt', force_reload=True)
  # kalman filter tracker
  tracker = cv2.TrackerCSRT_create()  # 創建追蹤器
  tracking = False 
  main = []
  with mp_face_mesh.FaceMesh(
      max_num_faces=1,
      refine_landmarks=True,
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5) as face_mesh:
    while cap.isOpened():
      success, image = cap.read()
      if not success:
        print("Ignoring empty camera frame.")
        # If loading a video, use 'break' instead of 'continue'.
        continue
      
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
      
      if tracking:
        success, point = tracker.update(image)
        if success:
            p1 = [int(point[0]), int(point[1])]
            p2 = [int(point[0] + point[2]), int(point[1] + point[3])]
            cv2.rectangle(image, p1, p2, (0, 0, 255), 3)
            cv2.putText(image, 'main', p1, cv2.FONT_HERSHEY_SIMPLEX,
                  1, (0, 0, 255), 1, cv2.LINE_AA)
      else:

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        imgh = image.shape[0]
        imgw = image.shape[1]

        results = face_mesh.process(image)
        # Draw the face mesh annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)


        if results.multi_face_landmarks:
          for face_landmarks in results.multi_face_landmarks:
            
            # line the face
            face_list = face_rec(face_landmarks, imgw, imgh)
            cv2.line(image, (face_list[0], face_list[1]), (face_list[2], face_list[3]), (255, 255, 0), 2)
            cv2.line(image, (face_list[4], face_list[5]), (face_list[6], face_list[7]), (255, 255, 0), 2)
            cv2.line(image, (face_list[0], face_list[1]), (face_list[4], face_list[5]), (255, 255, 0), 2)
            cv2.line(image, (face_list[2], face_list[3]), (face_list[6], face_list[7]), (255, 255, 0), 2)
        
            yolo = model(image)
            df = yolo.pandas().xyxy[0]
            mask = df['name'].eq('person')
            #person_rows = df[mask] 
            xmin = df[mask]['xmin'].values
            ymin = df[mask]['ymin'].values
            xmax = df[mask]['xmax'].values
            ymax = df[mask]['ymax'].values
            for x1, y1, x2, y2 in zip(xmin, ymin, xmax, ymax):
              cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
              if x1 <= face_list[0] and y1 <= face_list[1] and x2 >= face_list[6] and y2 >= face_list[7]:
                cv2.putText(image, 'main', (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX,
                  1, (255, 0, 0), 1, cv2.LINE_AA)
                main = [int(x1), int(y1), int(abs(x1 - x2)), int(abs(y1 - y2))]
              else:
                cv2.putText(image, 'person', (int(x1), int(y1)), cv2.FONT_HERSHEY_SIMPLEX,
                  1, (255, 0, 0), 1, cv2.LINE_AA)
      # Flip the image horizontally for a selfie-view display.
      #cv2.imshow('MediaPipe Face Mesh', cv2.flip(image, 1))
      cv2.imshow('MediaPipe Face Mesh', image)
      if cv2.waitKey(1) & 0xFF == 27:
        break
      if cv2.waitKey(1) & 0xFF == 32:
        tracker.init(image, main)
        tracking = True
    cap.release()
    cv2.destroyAllWindows()


if __name__=='__main__':
    webcam_input()