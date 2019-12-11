import snowboydecoder
import sys
import signal
import speech_recognition as sr
import os
import aiui
import audiofileinput as ggas
import socket

"""
This demo file shows you how to use the new_message_callback to interact with
the recorded audio after a keyword is spoken. It uses the speech recognition
library in order to convert the recorded audio into text.

Information on installing the speech recognition library can be found at:
https://pypi.python.org/pypi/SpeechRecognition/
"""


host = 'localhost'        # set ip
port = 2001                 # Set port
interrupted = False
model_flag = 0;

def audioRecorderCallback(fname):
    global model_flag
    print("converting audio to text")
    r = sr.Recognizer()
    with sr.AudioFile(fname) as source:
        audio = r.record(source)  # read the entire audio file
    print("thinking...")
    socketSend('ON_S2')  
    if(model_flag == 1):             #iflytek aiui
        try:
            aiui.main(fname)
        except:
            print("aiui err") 
    elif(model_flag == 2):           #Google Assistant
        try:
            os.system("~/env/bin/python3 audiofileinput.py -i "+fname + " -o test.wav")
        except:
            print("Google assistant error")
    socketSend('ON_S1')       
    model_flag = 0
    os.remove(fname)
    print('listening')
    
def socketSend(data):
    try:        
        s = socket.socket()
        s.connect((host, port))           # connect serve
        s.send(data.encode('utf-8'))      # recieve data
        s.close()
    except:
        print("socket error") 
        
def detectedCallback1():
    global model_flag
    model_flag = 1
    snowboydecoder.play_audio_file()
    print('recording audio...', end='', flush=True)
    
def detectedCallback2():
    global model_flag
    model_flag = 2
    snowboydecoder.play_audio_file()
    print('recording audio...', end='', flush=True)
    
def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) != 3:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

models = sys.argv[1:]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

sensitivity = [0.5]*len(models)
detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity)
callbacks = [lambda: detectedCallback1(),
             lambda: detectedCallback2()]
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=callbacks,
               audio_recorder_callback=audioRecorderCallback,
               interrupt_check=interrupt_callback,
               silent_count_threshold=0.1,
               sleep_time=0.01)

detector.terminate()




