import socket
import os
import wave
from struct import pack
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from nlp import get_similar
from ros.sum import sheilta
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/home/itamar/ninispeech/keys/algo-demo-538170d1acf3.json"

client = speech.SpeechClient()



def save_wav(data, path):
    #audio_data_bytes = pack('<' + ('h' * len(data)), *data)

    RATE = 16000
    WIDTH = 2
    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(WIDTH)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()

def recv_chunks(sock):
    audio_buffer = bytes()
    audio_time = 0
    chunk_size = 1280
    RATE = 16000
    MAX_TIME = 50000
    WIDTH = 2
    while audio_time <= MAX_TIME:
        data = sock.recv(1280)
        yield data
        # data, addr = s.recvfrom(1280)
        audio_buffer += data
        audio_time += (chunk_size / float(WIDTH)) * (1 / float(RATE))
    print("DONE")
    print(len(audio_buffer))
    save_wav(audio_buffer, 'tcp_stream.wav')




def put_command(text, opcode = - 1, result_data = ""):
    with open('website/currentCommand.txt', 'w') as f:
        if opcode == -1:
            print("writing:", text)
            f.write(text)
        else:
            print("writing text and opcode:", text, opcode)
            f.write(text + "\n" + str(opcode))
    if len(result_data) > 0:
        with open('website/result.txt', 'w') as f:
            f.write(result_data)


if __name__ == "__main__":
    # print(get_similar('תביעות נזיקין'))
    # exit()
    #UDP_IP = "172.16.2.73"
    UDP_IP = "192.168.43.18"
    UDP_PORT = 5006

    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the socket to a public host, and a well-known port
    serversocket.bind((UDP_IP, UDP_PORT))
    # become a server socket
    serversocket.listen(5)
    print("waiting for connections...")
    while True:
        try:
            (clientsocket, address) = serversocket.accept()
            print("connected with:", address)

            client = speech.SpeechClient()
            print("A")
            requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                        for chunk in  recv_chunks(clientsocket))
            print("B")
            config = types.RecognitionConfig(
                encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,

                language_code='he-IL')
            print("C")
            streaming_config = types.StreamingRecognitionConfig(config=config)

            def get_text_stream():
                responses = client.streaming_recognize(streaming_config, requests)
                # [END migration_streaming_request]
                print("D")
                for response in responses:
                    print("E")
                    # Once the transcription has settled, the first result will contain the
                    # is_final result. The other results will be for subsequent portions of
                    # the audio.
                    for result in response.results:
                       # print('Finished: {}'.format(result.is_final))
                        #print('Stability: {}'.format(result.stability))
                        alternatives = result.alternatives
                        # The alternatives are ordered from most likely to least.
                        for alternative in alternatives:
                            yield alternative.transcript
                            #print('Confidence: {}'.format(alternative.confidence))
                           # print('Transcript: {}'.format(alternative.transcript))


            unprocessed_text = ""
            for text in get_text_stream():
                unprocessed_text += text
                print(unprocessed_text)
                keyswords_judge = ['שופטת', 'שופט']
                if any(kw in unprocessed_text for kw in keyswords_judge):
                    print("JUDGE")
                    if 'יעל' in unprocessed_text:
                        put_command(unprocessed_text, 1)
                    unprocessed_text = ""
                keywords_prev = ['תקדים']
                if all([kw in unprocessed_text for kw in keywords_prev]):
                    print("TAKDIM")
                    query_text = unprocessed_text[unprocessed_text.index(keywords_prev[0]) + len(keywords_prev[0]) : ]
                    print("query:" , query_text)
                    similar_psakim = get_similar(query_text)
                    put_command(unprocessed_text, 3, str(similar_psakim))
                    unprocessed_text = ""
                keywords_ros = ['חוק']
                if all([kw in unprocessed_text for kw in keywords_ros]):
                    print("ROS")
                    query_text = unprocessed_text
                    print("query:" , query_text)
                    all_text = sheilta(query_text)
                    N_WORDS_ = 100
                    all_text = " ".join(all_text.split()[:N_WORDS_])
                    put_command(unprocessed_text, 2, all_text)
                    unprocessed_text = ""
                #put_command(unprocessed_text)
                #unprocessed_text = ""
        except Exception as e:
            print(e)