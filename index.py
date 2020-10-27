#coding=utf-8
#!/usr/bin/env python3
from bottle import get,post,run,request,template,static_file,route
import RPi.GPIO as GPIO
import time
import subprocess
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')

# L298N引脚接GPIO
IN1 = 11
IN2 = 12
IN3 = 13
IN4 = 15
ENA = 16
ENB = 18

def open_video():
    command = 'mjpg_streamer -i "input_raspicam.so" -o "output_http.so -p 8888 -w /usr/local/www" -b'
    subprocess.Popen(command, shell=True)

def init():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(IN1,GPIO.OUT)
    GPIO.setup(IN2,GPIO.OUT)
    GPIO.setup(IN3,GPIO.OUT)
    GPIO.setup(IN4,GPIO.OUT)
# 前进
def forward(tf):
    GPIO.output(IN1,GPIO.LOW)
    GPIO.output(IN2,GPIO.HIGH)
    GPIO.output(IN3,GPIO.LOW)
    GPIO.output(IN4,GPIO.HIGH)
    time.sleep(tf)
    GPIO.cleanup()
# 后退
def down(tf):
    GPIO.output(IN1,GPIO.HIGH)
    GPIO.output(IN2,GPIO.LOW)
    GPIO.output(IN3,GPIO.HIGH)
    GPIO.output(IN4,GPIO.LOW)
    time.sleep(tf)
    GPIO.cleanup()
# 左转弯
def left(tf):
    GPIO.output(IN1,False)
    GPIO.output(IN2,False)
    GPIO.output(IN3,GPIO.HIGH)
    GPIO.output(IN4,GPIO.LOW)
    time.sleep(tf)
    GPIO.cleanup()
# 右转弯
def right(tf):
    GPIO.output(IN1,GPIO.HIGH)
    GPIO.output(IN2,GPIO.LOW)
    GPIO.output(IN3,False)
    GPIO.output(IN4,False)
    time.sleep(tf)
    GPIO.cleanup()
# 停止
def stop():
    GPIO.output(IN1,False)
    GPIO.output(IN2,False)
    GPIO.output(IN3,False)
    GPIO.output(IN4,False)
    GPIO.cleanup()

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static')

@get("/")
def index():
    currentPath=os.path.dirname(os.path.realpath(__file__)) #获取当前路径
    return template(currentPath+"/index")
    
@post("/cmd")
def cmd():
    print("按下了按钮: "+request.body.read().decode())
    init()
    sleep_time = 1
    arg = request.body.read().decode()
    if(arg=='up'):
        print("前进了: "+request.body.read().decode())
        forward(sleep_time)
    elif(arg=='down'):
        print("后退了: "+request.body.read().decode())
        down(sleep_time)
    elif(arg=='left'):
        print("左转了: "+request.body.read().decode())
        left(sleep_time)
    elif(arg=='right'):
        print("右转了: "+request.body.read().decode())
        right(sleep_time)
    elif(arg=='stop'):
        print("停止了: "+request.body.read().decode())
        stop() 
    elif(arg=='video'):
        print("打开视频: "+request.body.read().decode())
        open_video()           
    else:
        return False
    #return "OK"
    
run(host="0.0.0.0",port="8080")


#forward(1)
#GPIO.cleanup()