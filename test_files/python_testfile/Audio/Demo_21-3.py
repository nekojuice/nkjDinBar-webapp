# -*- coding: utf-8 -*-

import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np



def record(duration_sec, fs):
    ''' Record duration_sec with sampling rate fs '''
    
    chunk = 2048
    p = pyaudio.PyAudio()
    stream = p.open( format=pyaudio.paFloat32, channels=1, rate=fs, input=True, frames_per_buffer=chunk)
    speech = []
    print('Start recording...')
    for i in range(int(duration_sec*fs/chunk)):
        reading_samples = np.frombuffer(stream.read(chunk), dtype = np.float32).tolist()
        speech.extend(reading_samples)
    print('Finished!')
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    return np.asarray(speech).astype(np.float32)


def play_raw(speech, fs):
    ''' Play audio raw data '''

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=fs, output=True)
    stream.write(speech.tostring())
    stream.stop_stream()
    stream.close()
    p.terminate()


def save_wav(speech, fs):
    ''' Save as wav file '''
    
    wf = wave.open('record.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(fs)
    wf.writeframes(b''.join((speech*32768).astype(np.int16)))
    wf.close()
    print('Done: record.wav')
    
    
''' Main '''

# 使用麥克風錄音
fs = 16000          # 欲使用的取樣率
duration_sec = 5    # 要錄幾秒
speech = record(duration_sec, fs)

# 繪製波型
plt.figure(figsize=(10, 5))
plt.plot(speech)
plt.xlabel('samples')
plt.ylabel('amplitude')
plt.show()

# 播放音檔
play_raw(speech, fs)

# 輸出音檔
save_wav(speech, fs)