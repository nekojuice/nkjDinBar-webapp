import zmq
import cv2
import base64

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://0.0.0.0:5000")

camera = cv2.VideoCapture(0)
#camera = cv2.VideoCapture(0, apiPreference=cv2.CAP_V4L)

# 控制相機(視訊串流)
def gen_frames():
    try:
        while True:
            success, frame = camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    except KeyboardInterrupt:
        print('關閉相機')
        camera.stop()


while True:
    try:
        (grabbed, frame) = camera.read()  # grab the current frame
        #frame = cv2.resize(frame, (640, 480))  # resize the frame
        encoded, buffer = cv2.imencode('.jpg', frame)
        socket.send_string(base64.b64encode(buffer))
        
    except KeyboardInterrupt:
        camera.release()
        cv2.destroyAllWindows()
        print("串流結束")
        break