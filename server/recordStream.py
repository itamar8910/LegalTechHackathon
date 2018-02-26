import socket

from sys import byteorder
from array import array
from struct import pack
import numpy as np
import pyaudio
import wave
import sys
import pickle
THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 16000
MAX_REC_TIME = 12

def is_silent(snd_data):
    "Returns 'True' if below the 'silent' threshold"
    return max(snd_data) < THRESHOLD

def normalize(snd_data):
    "Average the volume out"
    MAXIMUM = 16384
    times = float(MAXIMUM)/max(abs(i) for i in snd_data)

    r = array('h')
    for i in snd_data:
        r.append(int(i*times))
    return r

def trim(snd_data):
    "Trim the blank spots at the start and end"
    def _trim(snd_data):
        snd_started = False
        r = array('h')

        for i in snd_data:
            if not snd_started and abs(i)>THRESHOLD:
                snd_started = True
                r.append(i)

            elif snd_started:
                r.append(i)
        return r

    # Trim to the left
    snd_data = _trim(snd_data)

    # Trim to the right
    snd_data.reverse()
    snd_data = _trim(snd_data)
    snd_data.reverse()
    return snd_data

def add_silence(snd_data, seconds):
    "Add silence to the start and end of 'snd_data' of length 'seconds' (float)"
    r = array('h', [0 for i in range(int(seconds*RATE))])
    r.extend(snd_data)
    r.extend([0 for i in range(int(seconds*RATE))])
    return r

def start_stream(pyaudio_obj):

    stream = pyaudio_obj.open(format=FORMAT, channels=1, rate=RATE,
                    input=True, output=True,
                    frames_per_buffer=CHUNK_SIZE)
    return stream

def record(stream, pyaudio_obj):
    """
    Record a word or words from the microphone and
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the
    start and end, and pads with 0.5 seconds of
    blank sound to make sure VLC et al can play
    it without getting chopped off.
    """
    # p = pyaudio.PyAudio()
    # stream = p.open(format=FORMAT, channels=1, rate=RATE,
    #     input=True, output=True,
    #     frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')
    rec_time = 0

    while rec_time <= MAX_REC_TIME:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(normalize(snd_data))

        silent = is_silent(snd_data)

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True
        rec_time += CHUNK_SIZE / float(RATE)
        yield snd_data
        # if snd_started and num_silent > 30:
        #     break
    print("DONE RECORDING")
    sample_width = pyaudio_obj.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    pyaudio_obj.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5)
    #return sample_width, r

def stream_through_socket(path, sock):
    "Records from the microphone and outputs the resulting data to 'path'"
    data = []
    pyaudio_obj = pyaudio.PyAudio()
    sample_width = pyaudio_obj.get_sample_size(FORMAT)
    #print(sample_width)
    for chunk_data in record(start_stream(pyaudio_obj), pyaudio_obj):
        data.extend(chunk_data)
        #print(sys.getsizeof(pickle.dumps(chunk_data)))
        #print(chunk_data)
        sock.sendall(pickle.dumps(chunk_data))

        #print("got chunk")
    #print("data len:", len(data))
    data = pack('<' + ('h'*len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 55822))

    print("please speak a word into the microphone")
    stream_through_socket('demo.wav', s)
    s.close()
    print("done - result written to demo.wav")