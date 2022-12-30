# https://gist.github.com/mirfan899/4dec738636c711d378eac1793ec95329
#!/usr/bin/env python

import pyaudio
import socket
import sys


def audio_receive():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 8000
    CHUNK = 2048

    host_ip = '192.168.137.10'
    port = 9999
    socket_address = (host_ip,port)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(socket_address)
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

    try:
        while True:
            data = s.recv(CHUNK)
            stream.write(data)
    except KeyboardInterrupt:
        pass

    print('Shutting down')
    s.close()
    stream.close()
    audio.terminate()