# -*- coding: utf-8 -*-
# 下载安装完百度sdk后，在aip文件夹旁边新建此py文件
from aip import AipSpeech
# 准备调用树莓派GPIO接口
import RPi.GPIO as GPIO
# 可以在python中执行Linux命令行
import os
import time
import json

# 使用BCM方式来调用树莓派针脚
GPIO.setmode(GPIO.BCM)


class Speak:
    def __init__ (self,message,times,launguage,isRemove):
        '''
        传入参数　消息　次数　是否清除合成的语音文件
        '''
        self.tts(message,launguage)
        #说几次
        for i in range(0,times):
            self.say()
        if isRemove:
            self.over()
    def tts(self,message,launguage):
        try:
            import requests
        except:
            print ("请下载python-requests模块后使用...")
            exit(-1)
        import urllib
        s = requests.Session()
        mes=''
        if launguage is "zh":
            mes="http://tts.baidu.com/text2audio?lan=zh&pid=101&vol=9&ie=UTF-8&text="
        else:
            mes="http://tts.baidu.com/text2audio?lan=en&pid=101&vol=9&ie=UTF-8&text="
        s.get(mes+ urllib.quote(message))
        res = s.get(mes+ urllib.quote(message)).content
        f = open("tts-temp.mp3", "w")
        f.write(res)
        f.close()
    def say(self):
        os.system("play tts-temp.mp3")
    def over(self):
        os.system("rm tts-temp.mp3")
    def play(music):
        os.system("play "+music)

# man=Speak("你好 中国",1,"zh",True)
# 录音为wav格式音频文件，然后转换为pcm格式
def makePCM():
    # 录音，"plughw:1,0"表示从USB话筒设备录音，这句命令最终录制完的格式就是百度要求的16k音质
    os.system('sudo arecord -D "plughw:1,0" -f S16_LE -d 3 -r 16000 voiceAction.wav')
    print('完成3秒录音')
    # 用ffmpeg方法转换格式
    os.system('sudo ffmpeg -y -i voiceAction.wav -acodec pcm_s16le -f s16le -ac 1 -ar 16000 voiceAction.pcm')
    print('完成pcm转换')


# 读取本地音频文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


# 获取语音识别结果
def getVoiceText():
    makePCM()
    # 初始化 API KEY,SECRET KEY,APP ID
    # 这些值需要在http://ai.baidu.com注册账号，登录后在百度云管理中心可以找到
    apiKey = 'Ea0wshcH0wFnvPH87stEEt4u'
    secretKey = '1tkgwGyNivBheEuSh6Sjm67h0CDcVUYP'
    appID = '18896438'

    # 调用百度sdk文件的AipSpeech方法进行token验证
    client = AipSpeech(appID, apiKey, secretKey)

    if os.path.exists('voiceAction.pcm'):
        # 上传voiceAction.pcm文件到百度服务器进行语音识别
        result = client.asr(get_file_content('voiceAction.pcm'), 'pcm', 16000, {
            'lan': 'zh',
        })

        # 用json方式返回数据
        json_result = json.dumps(result)
        strtestObj = json.loads(json_result)
        try:
            # 得到语音识别后的结果
            lists = strtestObj["result"]
            print
            lists[0]
            return lists[0]
        except KeyError:
            return False

    else:
        return False


# 初始化超声波传感器使用到的树莓派针脚
Trig_Pin_right = 23
Echo_Pin_right = 24
Trig_Pin_left = 17
Echo_Pin_left = 27
# 右超声波传感器针脚，输出电频
GPIO.setup(Trig_Pin_right, GPIO.OUT)
# 右超声波传感器针脚，接收信号
GPIO.setup(Echo_Pin_right, GPIO.IN)
# 左超声波传感器针脚，输出电频
GPIO.setup(Trig_Pin_left, GPIO.OUT)
# 左超声波传感器针脚，接收信号
GPIO.setup(Echo_Pin_left, GPIO.IN)

# 初始化小车四个电机和轮子所使用的针脚
right_IN1 = 11
right_IN2 = 12
left_IN3 = 13
left_IN4 = 15
# 全部设置为电频输出
GPIO.setup(right_IN1, GPIO.OUT)
GPIO.setup(right_IN2, GPIO.OUT)
GPIO.setup(left_IN3, GPIO.OUT)
GPIO.setup(left_IN4, GPIO.OUT)
# 频率都设置为100%
move_right_1 = GPIO.PWM(right_IN1, 100)
move_right_2 = GPIO.PWM(right_IN2, 100)
move_left_3 = GPIO.PWM(left_IN3, 100)
move_left_4 = GPIO.PWM(left_IN4, 100)

# 开始启动时都设为0%
move_right_1.start(0)
move_right_2.start(0)
move_left_3.start(0)
move_left_4.start(0)


def forword():
    # 让小车前进
    move_right_1.start(60)
    move_right_2.start(0)
    move_left_3.start(60)
    move_left_4.start(0)
    # 把输出频率设置为60%让小车慢慢跑，因为百度语音识别需要上传到服务器然后再回传到本地
    # 大概耗时3秒左右，跑太快的话小车可能来不及完成指令就撞墙，虽然有超声波避障。


def reverse():
    # 让小车后退
    move_right_1.start(0)
    move_right_2.start(100)
    move_left_3.start(0)
    move_left_4.start(100)


def turnLeft():
    # 让小车左转弯
    move_right_1.start(100)
    move_right_2.start(0)
    move_left_3.start(30)
    move_left_4.start(0)


def turnRight():
    # 让小车右转
    move_right_1.start(30)
    move_right_2.start(0)
    move_left_3.start(100)
    move_left_4.start(0)


def stop():
    # 小车停止
    move_right_1.stop()
    move_right_2.stop()
    move_left_3.stop()
    move_left_4.stop()


def getRightDistance():
    # 右超声波传感器获取距离
    GPIO.output(Trig_Pin_right, GPIO.LOW)
    time.sleep(0.002)
    GPIO.output(Trig_Pin_right, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(Trig_Pin_right, GPIO.LOW)
    while GPIO.input(Echo_Pin_right) == 0:
        pass
    t1 = time.time()
    while GPIO.input(Echo_Pin_right) == 1:
        pass
    t2 = time.time()
    return (t2 - t1) * 340 * 100 / 2


def getLeftDistance():
    # 左超声波传感器获取距离
    GPIO.output(Trig_Pin_left, GPIO.LOW)
    time.sleep(0.002)
    GPIO.output(Trig_Pin_left, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(Trig_Pin_left, GPIO.LOW)
    while GPIO.input(Echo_Pin_left) == 0:
        pass
    t1 = time.time()
    while GPIO.input(Echo_Pin_left) == 1:
        pass
    t2 = time.time()
    return (t2 - t1) * 340 * 100 / 2


try:
    while True:
        print('开始录音')
        makePCM()
        print('结束录音和转换')
        if getVoiceText() == u'前进，':
            forword()

        if getVoiceText() == u'后退，':
            reverse()

        if getVoiceText() == u'左转弯，':
            turnLeft()

        if getVoiceText() == u'右转弯，':
            turnRight()

        if getVoiceText() == u'停下，':
            stop()

except KeyboardInterrupt:
    GPIO.cleanup()
