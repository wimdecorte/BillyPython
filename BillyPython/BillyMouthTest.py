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
speed = 37

# max frequency = 1600
frequency = 200

mh = Adafruit_MotorHAT(addr=0x60,freq=frequency)
mouth = mh.getMotor(MOTOR_MOUTH)
mouth.setSpeed(speed)

mouth.run(Adafruit_MotorHAT.BACKWARD)
time.sleep(.07)
mouth.run(Adafruit_MotorHAT.RELEASE)
