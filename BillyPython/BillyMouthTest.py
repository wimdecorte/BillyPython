import time
from datetime import datetime
from datetime import timedelta
import atexit
import os
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

MOTOR_MOUTH = 2

# recommended for auto-disabling motors on shutdown
def turnOffMotors():
    if mh is not None:
        mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

# and to make sure it runs when quitting the script
atexit.register(turnOffMotors)

# for billy bones: keep it low enough that the mouth doesn't 'clatter' when closing
speed = 100

# max frequency = 1600 Hz max, 40 Hz min
frequency = 90

mh = Adafruit_MotorHAT(addr=0x60,freq=frequency)
mouth = mh.getMotor(MOTOR_MOUTH)
mouth.setSpeed(speed)

for x in range(0,4):
    mouth.run(Adafruit_MotorHAT.BACKWARD)
    time.sleep(.4)
    mouth.run(Adafruit_MotorHAT.RELEASE)
    time.sleep(1)
