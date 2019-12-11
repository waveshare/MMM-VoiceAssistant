#-*- coding: utf-8 -*-
import sys
import requests
import time
import hashlib
import base64
import re
import struct
import os
import socket
import snowboydecoder
host = 'localhost'        # set ip
port = 2001                 # Set port

URL = "http://openapi.xfyun.cn/v2/aiui"
APPID = "5beaacac"
API_KEY = "4227d60d150c455db467b623d7ae183d"
AUE = "raw"   #lanme: mp3  raw: wav
AUTH_ID = "2337fdd0e195503e32f83ca46b2a0e94"
DATA_TYPE = "audio"
SAMPLE_RATE = "16000"
SCENE = "main"
RESULT_LEVEL = "complete"
LAT = "39.938838"
LNG = "116.368624"
#个性化参数，需转义
PERS_PARAM = "{\\\"auth_id\\\":\\\"2337fdd0e195503e32f83ca46b2a0e94\\\"}"

#FILE_PATH = "record.wav"

#tts
TTS_URL = "http://api.xfyun.cn/v1/service/v1/tts"
TTS_API_KEY ="babdc8ada7bcfd2ccf79a2a6119c8126"

def buildHeader():
    curTime = str(int(time.time()))
    param = "{\"result_level\":\""+RESULT_LEVEL+"\",\"auth_id\":\""+AUTH_ID+"\",\"data_type\":\""+DATA_TYPE+"\",\"sample_rate\":\""+SAMPLE_RATE+"\",\"scene\":\""+SCENE+"\",\"lat\":\""+LAT+"\",\"lng\":\""+LNG+"\"}"
    #使用个性化参数时参数格式如下：
    #param = "{\"result_level\":\""+RESULT_LEVEL+"\",\"auth_id\":\""+AUTH_ID+"\",\"data_type\":\""+DATA_TYPE+"\",\"sample_rate\":\""+SAMPLE_RATE+"\",\"scene\":\""+SCENE+"\",\"lat\":\""+LAT+"\",\"lng\":\""+LNG+"\",\"pers_param\":\""+PERS_PARAM+"\"}"
    paramBase64 = str(base64.b64encode(param.encode('utf-8')), 'utf-8')

    m2 = hashlib.md5()
    m2.update((API_KEY + curTime + paramBase64).encode('utf-8'))
    checkSum = m2.hexdigest()

    header = {
        'X-CurTime': curTime,
        'X-Param': paramBase64,
        'X-Appid': APPID,
        'X-CheckSum': checkSum,
    }
    return header

def readFile(filePath):
    binfile = open(filePath, 'rb')
    data = binfile.read()
    return data


def getHeader():
        curTime = str(int(time.time()))
        param = "{\"aue\":\""+AUE+"\",\"auf\":\"audio/L16;rate=16000\",\"voice_name\":\"xiaoyan\",\"engine_type\":\"intp65\"}"
        paramBase64 = str(base64.b64encode(param.encode('utf-8')), 'utf-8')
        m2 = hashlib.md5()
        m2.update((TTS_API_KEY + curTime + paramBase64).encode('utf-8'))
        checkSum = m2.hexdigest()
        header ={
                'X-CurTime':curTime,
                'X-Param':paramBase64,
                'X-Appid':APPID,
                'X-CheckSum':checkSum,
                'X-Real-Ip':'127.0.0.1',
                'Content-Type':'application/x-www-form-urlencoded; charset=utf-8',
        }
        return header

def writeFile(file, content):
    with open(file, 'wb') as f:
        f.write(content)
    f.close()


def main(FILE_PATH):
    r = requests.post(URL, headers=buildHeader(), data=readFile(FILE_PATH))
    dic_json = r.json()
    #print(r.content)
    for i in dic_json['data']:
        if(i['sub'] == "nlp" and i['intent'] != {}):
            try:
                text = i['intent']['answer']['text']
            except:
                text = "不明白你再说什么，你还是说中文吧"
            print('我 :'+i['intent']['text'])
            print('机器人 :'+text)
            s = socket.socket()         # creat socket
            s.connect((host, port))     # connect serve
            s.send(('我 :'+i['intent']['text']+'<br/>机器人 :'+text).encode('UTF-8'))          # recieve data
            s.close()                  # Close the connection

            r = requests.post(TTS_URL,headers=getHeader(),data={'text':text})
            contentType = r.headers['Content-Type']
            if contentType == "audio/mpeg":
                sid = r.headers['sid']
                if AUE == "raw":
                    writeFile("tts.wav", r.content)
                else :
                    writeFile("tts.mp3", r.content)
                #print "success, sid = " + sid
            else :
                print(r.text)
            snowboydecoder.play_audio_file("tts.wav")
            os.system("rm tts.wav")

            break
    else:
        print('没有检测到人声')

if __name__ == '__main__':
    main(sys.argv[1])
