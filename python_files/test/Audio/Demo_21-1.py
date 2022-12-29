# -*- coding: utf-8 -*-

import pyaudio
import wave
import matplotlib.pyplot as plt
import numpy as np


def read_wav(file_name):
    ''' Read one channel wav file as float data (-1~1) ''' 
    
    wf = wave.open(file_name, 'rb')
    params = wf.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    raw = wf.readframes(nframes)
    speech = np.frombuffer(raw, dtype=np.short)/32768
    
    print('[Info]')
    print('Sampling rate:', framerate, 'Hz')
    print('Duration:', len(speech)/framerate, 'sec')
    print('Channel:', nchannels)
    
    return speech.astype(np.float32), framerate


def play_raw(speech, fs):
    ''' Play audio raw data '''

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32, channels=1, rate=fs, output=True)
    stream.write(speech.tostring())
    stream.stop_stream()
    stream.close()
    p.terminate()


''' Main '''

# 讀取音檔
file_name = 'record.wav'
speech, fs = read_wav(file_name)

# 繪製波型
plt.figure(figsize=(10, 5))
plt.plot(speech)
plt.title(file_name)
plt.xlabel('samples')
plt.ylabel('amplitude')
plt.show()

# 播放音檔
play_raw(speech, fs)
