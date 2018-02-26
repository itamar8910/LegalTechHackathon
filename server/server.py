import socket
import pickle
import wave
# create an INET, STREAMing socket
import io
from threading import Thread

import pyaudio
from struct import pack
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import os
import array
import numpy as np
from google.cloud.speech_v1.proto.cloud_speech_pb2 import SpeechContext

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/home/itamar/ninispeech/keys/algo-demo-538170d1acf3.json"

def save_wav(data, path):
    RATE = 16000
    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

def stream_audio_chunks(sock, all_data):
    while True:
        #print("receiving")
        chunk_data = sock.recv(4096)

        if not chunk_data:
            break
        try:
            chunk_data = pickle.loads(chunk_data)
            all_data.extend(chunk_data)
            #chunk_bytes = np.array(chunk_data, dtype=np.int16).tobytes()

            yield chunk_data
        except Exception as e:
            print("stream generator exception:", e)
            continue
        #yield pack('<' + ('h' * len(chunk_data)), *chunk_data)
        #audio_data.extend(chunk_data)

def stt(wav_path, num_alts = 1, lang = "he-IL"):
    "returns: (list of STT alternatives, raw response object)"

    WANTED_SAMPLE_RATE = 16000

    # Instantiates a client
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    file_name = os.path.join(
        os.path.dirname(__file__),
        wav_path)

    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=WANTED_SAMPLE_RATE,
        max_alternatives = num_alts,
        enable_word_time_offsets = False,
        language_code=lang,
    )
    # Detects speech in the audio file
    response = client.recognize(config, audio)
   # print(response)

    if len(response.results) > 0:
        alts = ["" for x in range(num_alts)]

        for res_i in range(len(response.results)):
            for alt_i in range(min(num_alts, len(response.results[res_i].alternatives))):
                alts[alt_i] += response.results[res_i].alternatives[alt_i].transcript

        alts.extend(["" for x in range(num_alts - len(alts))])

        return alts
    return [""]

def handle_stt(audio_data, i):
    bytes_data = pack('<' + ('h' * len(audio_data)), *audio_data)
    path = "tmp_audio_{}.wav".format(i)
    save_wav(bytes_data, path)
    text = stt(path)[0]
    print("Text", text)

client = speech.SpeechClient()

config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=16000,
    language_code='he-IL')
streaming_config = types.StreamingRecognitionConfig(config=config)

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
serversocket.bind(('', 55822))
# become a server socket
serversocket.listen(5)
print("waiting for connections...")
(clientsocket, address) = serversocket.accept()

audio_data = []
tmp_audio_buffer = []
SEND_LEN = 3
tmp_audio_index = 0
for chunk in stream_audio_chunks(clientsocket, audio_data):
    tmp_audio_buffer.extend(chunk)
    if len(tmp_audio_buffer) / float(16000) >= SEND_LEN:
        #TODO: handle chunks that are cut in the middle of a word
        #handle_stt(tmp_audio_buffer, tmp_audio_index)
        thread = Thread(target=handle_stt, args=(tmp_audio_buffer, tmp_audio_index, ))
        thread.start()
        tmp_audio_buffer = []
        tmp_audio_index += 1
if len(tmp_audio_buffer) != 0:
    handle_stt(tmp_audio_buffer, tmp_audio_index)


# for x in stream_audio_chunks(clientsocket, audio_data):
#     print("a")
#
# requests = (types.StreamingRecognizeRequest(audio_content=chunk)
#                 for chunk in stream_audio_chunks(clientsocket, audio_data))
#
# responses = client.streaming_recognize(streaming_config, requests)
# #print(len(responses))
# for response in responses:
#     # Once the transcription has settled, the first result will contain the
#     # is_final result. The other results will be for subsequent portions of
#     # the audio.
#     for result in response.results:
#         print('Finished: {}'.format(result.is_final))
#         print('Stability: {}'.format(result.stability))
#         alternatives = result.alternatives
#         # The alternatives are ordered from most likely to least.
#         for alternative in alternatives:
#             print('Confidence: {}'.format(alternative.confidence))
#             print('Transcript: {}'.format(alternative.transcript))

print("Done with all audio")
#print("audio data len:", len(audio_data))
FORMAT = pyaudio.paInt16
sample_width = pyaudio.PyAudio().get_sample_size(FORMAT)
audio_data_bytes = pack('<' + ('h'*len(audio_data)), *audio_data)

RATE = 16000
wf = wave.open('srvr_audio_save.wav', 'wb')
wf.setnchannels(1)
wf.setsampwidth(2)
wf.setframerate(RATE)
wf.writeframes(audio_data_bytes)
wf.close()


#print(address)