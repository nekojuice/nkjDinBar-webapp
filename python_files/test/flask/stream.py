from flask import Flask, render_template, Response
from imutils.video import VideoStream
import cv2
import time

app = Flask(__name__)
camera = cv2.VideoCapture(0) #, apiPreference=cv2.CAP_V4L



# @app.route('/hello')
# def hello():
#     return 'hello flask'

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

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()


# cv2.destroyAllWindows()
# camera.stop()
