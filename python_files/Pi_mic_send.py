# https://gist.github.com/mirfan899/4dec738636c711d378eac1793ec95329
#!/usr/bin/env python

import pyaudio
import socket
import select


def audio_send():
    global stopflag
    stopflag = False
    
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 8000
    CHUNK = 2048

    audio = pyaudio.PyAudio()

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('', 9999))
    serversocket.listen(5)


    def callback(in_data, frame_count, time_info, status):
        for s in read_list[1:]:
            s.send(in_data)
        return (None, pyaudio.paContinue)


    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK, stream_callback=callback)
    # stream.start_stream()

    read_list = [serversocket]
    print("recording...")

    try:
        while True:
            readable, writable, errored = select.select(read_list, [], [])
            for s in readable:
                if s is serversocket:
                    (clientsocket, address) = serversocket.accept()
                    read_list.append(clientsocket)
                    print("Connection from", address)
                else:
                    data = s.recv(1024)
                    if not data:
                        read_list.remove(s)
            if stopflag:
                break
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)


    print("finished recording")

    serversocket.close()
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()