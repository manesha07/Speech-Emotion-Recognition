from emotion_recognition import EmotionRecognizer
import pyaudio
import os
import wave
from sys import byteorder
from array import array
from struct import pack
from sklearn.ensemble import GradientBoostingClassifier, BaggingClassifier
from utils import get_best_estimators
import os
import random
from scipy.io import wavfile


#For javascript variable
import json

from flask import request

from flask import Flask, render_template

app = Flask(__name__)

THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 16000

SILENCE = 5

global record
record = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/saveaudio', methods=['POST','GET'])
def saveaudio():
    global record
    if request.method == 'POST':
        files = request.files['file']
        files.save("sample.wav")
    record = True
    return "hello"

@app.route('/test1', methods=['POST','GET'] )
def test():
    global record
    if request.method == 'POST':
        files =request.files['upload']
        print(files)
        if record == False:
            files.save("sample.wav")
    estimators = get_best_estimators(True)
    estimators_str, estimator_dict = get_estimators_name(estimators)
    print(estimator_dict)
    import argparse
    parser = argparse.ArgumentParser(description="""
                                    Testing emotion recognition system using your voice,
                                    please consider changing the model and/or parameters as you wish.
                                    """)
    parser.add_argument("-e", "--emotions", help=
                                            """Emotions to recognize separated by a comma ',', available emotions are
                                            "neutral", "calm", "happy" "sad", "angry", "fear", "disgust", "ps" (pleasant surprise)
                                            and "boredom", default is "sad,neutral,happy"
                                            """, default="sad,neutral,happy")
    parser.add_argument("-m", "--model", help=
                                        """
                                        The model to use, 8 models available are: {},
                                        default is "BaggingClassifier"
                                        """.format(estimators_str), default="KNeighborsClassifier")

    # Parse the arguments passed
    args = parser.parse_args()

    features = ["mfcc", "chroma", "mel"]
    detector = EmotionRecognizer(estimator_dict[args.model], emotions=args.emotions.split(","), features=features, verbose=0)
    detector.train()
    # print("Test accuracy score: {:.3f}%".format(detector.test_score()*100))
    filename = "sample.wav"
    # record_to_file(filename)
    # print(filename)

    # output = request.get_json()
    # print(output) # This is the output that was stored in the JSON within the browser
    # result = json.loads(output) #this converts the json output to a python dictionary

    # play(result.blob)
    # record_to_file(filename,result)
    #timer starts here
    result = detector.predict(filename)
    #timer stops
    print(result)

    if result == 'sad':
        file1 = random.choice(os.listdir("Dataset/sad/"))
        file2 = 'Dataset/sad/'+file1
        os.system("start " + file2)

    elif result == 'happy':
        file1 = random.choice(os.listdir("Dataset/happy/"))
        file2 = 'Dataset/happy/'+file1
        os.system("start " + file2)

    else:
        file1 = random.choice(os.listdir("Dataset/dramatic"))
        file2 = 'Dataset/dramatic/'+file1
        os.system("start " + file2)

    # output = request.get_json()
    # print(output) # This is the output that was stored in the JSON within the browser
    # result = json.loads(output) #this converts the json output to a python dictionary
    # print("this res",result)
    # filename = "test.wav"
    # record_to_file(filename,result)
    return render_template('index.html',result=result)

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

def record():
    """
    Record a word or words from the microphone and 
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the 
    start and end, and pads with 0.5 seconds of 
    blank sound to make sure VLC et al can play 
    it without getting chopped off.
    """
    p = pyaudio.PyAudio()
    # data = wavfile.read('8734.wav')
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)

    num_silent = 0
    snd_started = False

    r = array('h')

    while 1:
        # little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()
        r.extend(snd_data)

        silent = is_silent(snd_data)

        if silent and snd_started:
            num_silent += 1
        elif not silent and not snd_started:
            snd_started = True
        if snd_started and num_silent > SILENCE:
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 4)
    return sample_width, r

def record_to_file(path,data2):
    "Records from the microphone and outputs the resulting data to 'path'"
    # sample_width, data = record()
    # print("ssss",sample_width)
    # data = pack('<' + ('h'*len(data)), *data)

    # file5 = app.run(debug=True)
    # print("poooo",file5)

    # output = request.get_json()
    # print(output) # This is the output that was stored in the JSON within the browser
    # result = json.loads(output)
    print("huuu",data2)
    print("pathhhh",path)
    fs,data = wavfile.read(data2)
    wf = wave.open('demo.wav', 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    # print("fdd1d", fs)
    print("fddd1",data)
    wf.writeframes(data)
    wf.close()

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(RATE)
    # print("fdd1d", fs)
    print("fddd",data)
    wf.writeframes(data)
    wf.close()


def get_estimators_name(estimators):
    result = [ '"{}"'.format(estimator.__class__.__name__) for estimator, _, _ in estimators ]
    return ','.join(result), {estimator_name.strip('"'): estimator for estimator_name, (estimator, _, _) in zip(result, estimators)}

def play(file):
    wf = wave.open(file, 'rb')
    p = pyaudio.PyAudio()
    # data = wavfile.read('8734.wav')
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
        input=True, output=True,
        frames_per_buffer=CHUNK_SIZE)
    data3 = wf.readframes(CHUNK_SIZE)

    while len(data3) > 0:
        stream.write(data3)
        data3 = wf.readframes(CHUNK_SIZE)
    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == "__main__":
    app.run(debug=True)
    # estimators = get_best_estimators(True)
    # estimators_str, estimator_dict = get_estimators_name(estimators)
    # print(estimator_dict)
    # import argparse
    # parser = argparse.ArgumentParser(description="""
    #                                 Testing emotion recognition system using your voice,
    #                                 please consider changing the model and/or parameters as you wish.
    #                                 """)
    # parser.add_argument("-e", "--emotions", help=
    #                                         """Emotions to recognize separated by a comma ',', available emotions are
    #                                         "neutral", "calm", "happy" "sad", "angry", "fear", "disgust", "ps" (pleasant surprise)
    #                                         and "boredom", default is "sad,neutral,happy"
    #                                         """, default="sad,neutral,happy")
    # parser.add_argument("-m", "--model", help=
    #                                     """
    #                                     The model to use, 8 models available are: {},
    #                                     default is "BaggingClassifier"
    #                                     """.format(estimators_str), default="KNeighborsClassifier")
    #
    # # Parse the arguments passed
    # args = parser.parse_args()
    #
    # features = ["mfcc", "chroma", "mel"]
    # detector = EmotionRecognizer(estimator_dict[args.model], emotions=args.emotions.split(","), features=features, verbose=0)
    # detector.train()
    # # print("Test accuracy score: {:.3f}%".format(detector.test_score()*100))
    # print("Please talk")
    # filename = "test.wav"
    # record_to_file(filename)
    # # print(filename)
    # #timer starts here
    # result = detector.predict(filename)
    # #timer stops
    # print(result)
    #
    # if result == 'sad':
    #     file1 = random.choice(os.listdir("Dataset/sad/"))
    #     file2 = 'Dataset/sad/'+file1
    #     os.system("start " + file2)
    # elif result == 'happy':
    #     file1 = random.choice(os.listdir("Dataset/happy/"))
    #     file2 = 'Dataset/happy/'+file1
    #     os.system("start " + file2)
    # else:
    #     file1 = random.choice(os.listdir("Dataset/dramatic"))
    #     file2 = 'Dataset/dramatic/'+file1
    #     os.system("start " + file2)

