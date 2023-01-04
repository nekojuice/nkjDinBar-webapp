import wave
import pyaudio
from pyaudio import PyAudio,paInt16
from PIL import ImageGrab
import numpy as np
import cv2
from moviepy.editor import *
from moviepy.audio.fx import all
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 8000
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
audio_record_flag = True
def callback(in_data, frame_count, time_info, status):
    wf.writeframes(in_data)
    if audio_record_flag:
        return (in_data, pyaudio.paContinue)
    else:
        return (in_data, pyaudio.paComplete)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                input=True,
                stream_callback=callback)


cap = cv2.VideoCapture(0)
width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# image = ImageGrab.grab()#獲得當前屏幕
# width = image.size[0]
# height = image.size[1]
print("width:", width, "height:", height)
# print("image mode:",image.mode)
k=np.zeros((width,height),np.uint8)

fourcc = cv2.VideoWriter_fourcc(*'XVID')  #編碼格式
video = cv2.VideoWriter('output.avi', fourcc, 11.0, (width, height))
#經實際測試，單線程下最高幀率爲10幀/秒，且會變動，因此選擇9.5幀/秒
#若設置幀率與實際幀率不一致，會導致視頻時間與音頻時間不一致

print("video recording!!!!!")
stream.start_stream()
print("audio recording!!!!!")
record_count = 0
while True:
    success, image = cap.read()
    img_rgb = ImageGrab.grab()
    cv2.imshow('frame',image)
    video.write(image)
    if cv2.waitKey(1) == ord('q'):
        break

audio_record_flag = False
while stream.is_active():
    time.sleep(1)

stream.stop_stream()
stream.close()
wf.close()
p.terminate()
print("audio recording done!!!!!")

video.release()
cv2.destroyAllWindows()
print("video recording done!!!!!")

print("video audio merge!!!!!")
audioclip = AudioFileClip("output.wav")
videoclip = VideoFileClip("output.avi")
videoclip2 = videoclip.set_audio(audioclip)
video = CompositeVideoClip([videoclip2])
video.write_videofile("test2.mp4",codec='mpeg4')