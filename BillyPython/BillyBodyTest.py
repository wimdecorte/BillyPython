
import time
from datetime import datetime
from datetime import timedelta
import atexit
import os
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor

MOTOR_BODY = 1

# recommended for auto-disabling motors on shutdown
def turnOffMotors():
    if mh is not None:
        mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
        mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

# and to make sure it runs when quitting the script
atexit.register(turnOffMotors)

# bones2 = 175 / 100 -- keep the bones at right angles with the surface
# fish orange to bread brown
# fish brown to bread orange

# bread orange to hat brown (motor 1, right)
# bread black to hat black (motor 1, left)

speed = 175

# max frequency = 1600 Hz, min = 24 Hz
# same frequency applies to all channels
frequency = 100

mh = Adafruit_MotorHAT(addr=0x60,freq=frequency)
body = mh.getMotor(MOTOR_BODY)
body.setSpeed(speed)


# determine if body uses backward or forward, change either the code or the wires to match
body.run(Adafruit_MotorHAT.BACKWARD)
time.sleep(1.5)
body.run(Adafruit_MotorHAT.RELEASE)

# try tail
time.sleep(1)
body.run(Adafruit_MotorHAT.FORWARD)
time.sleep(0.5)
body.run(Adafruit_MotorHAT.RELEASE)