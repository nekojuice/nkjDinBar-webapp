import subprocess as sp
import cv2
from pyaudio import PyAudio, paInt16
import os
import threading
import time
import wave
from ffmpy3 import FFmpeg


class VCR:
    def __init__(self, filename) -> None:
        '''
        filename: 檔名
        '''
        self.filename = filename
        if os.path.exists(filename+'.mp4'):
            os.remove(filename+'.mp4')
            
        self.framerate = 8000
        self.NUM_SAMPLES = 1000
        self.channels = 1
        self.sampWidth = 2
        self.my_buf = b''
        self.flag_read = True
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        if not self.cap.isOpened():
            print("攝影機開啟失敗")

        w, h = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fourCC = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter(filename + '.avi', self.fourCC, 40, (w, h))
        
        pa = PyAudio()
        self.stream = pa.open(format=paInt16,
                              channels = self.channels,
                              rate = self.framerate,
                              input=True,
                              frames_per_buffer = self.NUM_SAMPLES)

    
    
    def save_wave_file(self):
        '''寫入.wav'''
        with wave.open(self.filename+'.wav','wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.sampWidth)
            wf.setframerate(self.framerate)
            wf.writeframes(self.my_buf)
        print('音訊寫入完成')
        
    def collect_mp3(self):
        '''錄音'''
        while self.flag_read:
            string_audio_data = self.stream.read(self.NUM_SAMPLES)
            self.my_buf += string_audio_data
        self.stream.close()
        
    def collect_mp4(self):
        font = cv2.FONT_HERSHEY_COMPLEX
        txt = '按空白鍵開始'
        while True:
            isOpen, frame = self.cap.read()
            if not isOpen:
                break
            #cv2.putText(frame, txt, (30,150), font, 0.8, (0, 0, 255), 1)
            cv2.imshow('Stream', frame)
            self.out.write(frame)
            if cv2.waitKey(1) == ord(' '):
                break
        
        print("錄製開始")
        threading.Thread(target=self.collect_mp3).start()
        while True:
            isOpen, frame = self.cap.read()
            if not isOpen:
                break
            self.out.write(frame)
            cv2.imshow('frame', frame)
            
            if cv2.waitKey(1) == ord('q'):
                self.flag_read = False
                break
        
        self.out.release()
        self.cap.release()
        cv2.destroyAllWindows()
        
    def runMain(self):
        '''啟動位置'''
        threading.Thread(target=self.collect_mp4).start()
        while self.flag_read:
            time.sleep(5)
            
            print('準備寫入音訊')
            self.save_wave_file()
            
            print('準備將影音合成')
            FFmpeg(executable='D:/Application/ffmpeg/bin/ffmpeg.exe',
                   inputs={f'{self.filename}.avi':None, f'{self.filename}.wav':None},
                   outputs={f'{self.filename}.mp4':'-c:v h264 -c:a ac3'}).run()
            print('合成結束')
            
if __name__ == '__main__':
    v = VCR(filename='myaudio')
    v.runMain()