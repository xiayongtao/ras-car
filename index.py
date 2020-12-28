# coding=utf-8
# !/usr/bin/env python3
from bottle import get, post, run, request, template, static_file, route
import RPi.GPIO as GPIO
import subprocess
import sys
import os
import socket

import imp

imp.reload(sys)

# sys.setdefaultencoding('utf8')

# L298N引脚接GPIO
IN1 = 11
IN2 = 12
IN3 = 13
IN4 = 15
ENA = 16
ENB = 18

import threading
import smbus
import time

bus = smbus.SMBus(1)

i2c_addr = 0x0f  # 语音识别模块地址
asr_add_word_addr = 0x01  # 词条添加地址
asr_mode_addr = 0x02  # 识别模式设置地址，值为0-2，0:循环识别模式 1:口令模式 ,2:按键模式，默认为循环检测
asr_rgb_addr = 0x03  # RGB灯设置地址,需要发两位，第一个直接为灯号1：蓝 2:红 3：绿 ,#第二个字节为亮度0-255，数值越大亮度越高
asr_rec_gain_addr = 0x04  # 识别灵敏度设置地址，灵敏度可设置为0x00-0x7f，值越高越容易检测但是越容易误判，
# 建议设置值为0x40-0x55,默认值为0x40

asr_clear_addr = 0x05  # 清除掉电缓存操作地址，录入信息前均要清除下缓存区信息
asr_key_flag = 0x06  # 用于按键模式下，设置启动识别模式
asr_voice_flag = 0x07  # 用于设置是否开启识别结果提示音
asr_result = 0x08  # 识别结果存放地址
asr_buzzer = 0x09  # 蜂鸣器控制寄存器，1位开，0位关
asr_num_cleck = 0x0a  # 录入词条数目校验


def AsrAddWords(idnum, str):
    global i2c_addr
    global asr_add_word_addr
    words = []
    words.append(idnum)
    for alond_word in str:
        words.append(ord(alond_word))

    print(words)
    bus.write_i2c_block_data(i2c_addr, asr_add_word_addr, words)  # 第三个参数list，元素小于30个
    time.sleep(0.3)


def I2CReadByte(reg):
    global i2c_addr
    bus.write_byte(i2c_addr, reg)
    time.sleep(0.05)
    Read_result = bus.read_byte(i2c_addr)
    return Read_result


def asr_init():
    print("开始初始化语音...")
    bus.write_byte_data(i2c_addr, asr_clear_addr, 0x40)  # 清除掉电缓存区
    time.sleep(12)  # 必须有足够的清除时间，约11-12s
    bus.write_byte_data(i2c_addr, asr_mode_addr, 0x01)  # 设置为口令模式，口令为“小博”
    time.sleep(0.1)
    AsrAddWords(0, "xiao bo")
    AsrAddWords(1, "qian jin")
    AsrAddWords(2, "hou tui")
    AsrAddWords(3, "zuo zhuan")
    AsrAddWords(4, "you zhuan")
    AsrAddWords(5, "ting zhi")

    bus.write_byte_data(i2c_addr, asr_rec_gain_addr, 0x50)  # 设置灵敏度，建议值为0x40-0x55
    time.sleep(0.1)
    bus.write_byte_data(i2c_addr, asr_voice_flag, 1)  # 设置开关提示音
    print("语音初始化完成！")


def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)
    asr_init()
    open_video()


# 前进
def forward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)


# 后退
def down():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)


# 左转弯
def left():
    GPIO.output(IN1, False)
    GPIO.output(IN2, False)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)


# 右转弯
def right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, False)
    GPIO.output(IN4, False)


# 停止
def stop():
    GPIO.output(IN1, False)
    GPIO.output(IN2, False)
    GPIO.output(IN3, False)
    GPIO.output(IN4, False)


@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static')


@get("/")
def index():
    currentPath = os.path.dirname(os.path.realpath(__file__))  # 获取当前路径
    return template(currentPath + "/index")


def open_video():
    command = 'mjpg_streamer -i "input_raspicam.so" -o "output_http.so -p 8888 -w /usr/local/www" -b'
    subprocess.Popen(command, shell=True)
    localIp = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
    return {'url': 'http://' + localIp + ':8888/?action=stream'}


def stop_video():
    subprocess.Popen.terminate()


@post("/cmd")
def cmd():
    print("按下了按钮: " + request.body.read().decode())
    arg = request.body.read().decode()
    if (arg == 'up'):
        print("前进了: " + request.body.read().decode())
        forward()
    elif (arg == 'down'):
        print("后退了: " + request.body.read().decode())
        down()
    elif (arg == 'left'):
        print("左转了: " + request.body.read().decode())
        left()
    elif (arg == 'right'):
        print("右转了: " + request.body.read().decode())
        right()
    elif (arg == 'stop'):
        print("停止了: " + request.body.read().decode())
        stop()
    elif (arg == 'video_play'):
        print("打开视频: " + request.body.read().decode())
        return open_video()
    elif (arg == 'video_stop'):
        print("关闭视频: " + request.body.read().decode())
        stop_video()
    else:
        return False


# return "OK"

def action(act):
    if (act == 1):
        forward()
        time.sleep(1)
        stop()
    elif (act == 2):
        down()
        time.sleep(1)
        stop()
    elif (act == 3):
        left()
        time.sleep(1)
        stop()
    elif (act == 4):
        right()
        time.sleep(1)
        stop()
    else:
        stop()


def asr_run(n):
    print("task", n)
    while True:
        result = I2CReadByte(asr_result)
        print("result:", result)
        action(result)
        time.sleep(0.01)

GPIO.cleanup()
init()

threading.Thread(target=asr_run, args=("asr",)).start()
run(host="0.0.0.0", port="8080")
GPIO.cleanup()

