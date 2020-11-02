# coding=utf-8
# !/usr/bin/env python3
from bottle import get, post, run, request, template, static_file, route
import RPi.GPIO as GPIO
import subprocess
import sys
import os
import socket

reload(sys)
sys.setdefaultencoding('utf8')

# L298N引脚接GPIO
IN1 = 11
IN2 = 12
IN3 = 13
IN4 = 15
ENA = 16
ENB = 18


def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(IN1, GPIO.OUT)
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)
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


init()
run(host="0.0.0.0", port="8080")
GPIO.cleanup()
