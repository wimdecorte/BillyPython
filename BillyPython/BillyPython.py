# import ptvsd
import fmrest
import time
import atexit
import os
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import configparser
from multiprocessing import Process
import vlc

MOTOR_HEAD_TAIL = 1
MOTOR_MOUTH = 2

# get the config file
myfile = __file__
mydir = os.path.dirname(myfile)
Config = configparser.ConfigParser()
Config.read(os.path.join(mydir, 'billy.ini'))

# ptvsd.enable_attach(secret='1803')

# recommended for auto-disabling motors on shutdown
def turnOffMotors():
    if mh is not None:
        mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

# and to make sure it runs when quitting the script
atexit.register(turnOffMotors)

# function to tilt head up when the fish talks
def head_tilt():
    while True:
        head.run(Adafruit_MotorHAT.BACKWARD)
        # set to forward to move the tail
        time.sleep(5)
        head.run(Adafruit_MotorHAT.RELEASE)

# function to tilt head up when the fish talks
def waggle_tail():
    while True:
        head.run(Adafruit_MotorHAT.FORWARD)
        # set to forward to move the tail
        time.sleep(5)
        head.run(Adafruit_MotorHAT.RELEASE)

# make the connection to the FMS Data API
fms = fmrest.Server(Config.get('FMS', 'url'),
                        user=Config.get('FMS', 'user'),
                        password=Config.get('FMS', 'pw'),
                        database=Config.get('FMS', 'file'),
                        layout=Config.get('FMS', 'layout'))

token = fms.login()
# print(token)

# hook into the motor hat
mh = Adafruit_MotorHAT(addr=0x60,freq=70)

# while True:

# find the todo records
find_request = [{'flag_ready': '1'}]
try:
    foundset = fms.find(query=find_request)
except FileMakerError as Argument:
    print(Argument)
#except Exception as Argument:
#    print('need to figure out what error to use ' + Argument)

#if foundset is None:
#    # break and continue the loop
#    print('nothing found in FMS')
#    # break
#else:
#    todo = foundset[0]
#    old_notes = todo.notes
#    print(old_notes)



mouth = mh.getMotor(MOTOR_MOUTH)
mouth.setSpeed(100)
mouth.run(Adafruit_MotorHAT.RELEASE)

head =  mh.getMotor(MOTOR_HEAD_TAIL)
head.setSpeed(100)
head.run(Adafruit_MotorHAT.RELEASE)

if True:
    print("This will test the Billy Bass motors")
    print("The head will tilt up, and the mouth should move several times")
    p = Process(target=head_tilt)
    # p.start()

    for x in range(0,4):
        # move the mouth
        # mouth.run(Adafruit_MotorHAT.BACKWARD)
        time.sleep(1)
        # mouth.run(Adafruit_MotorHAT.RELEASE)
        time.sleep(1)

    # p.terminate()
    print("Test Complete")

# may need to do this in its own process? background
player = vlc.MediaPlayer('path to mp3')
player.play()
player.stop()
