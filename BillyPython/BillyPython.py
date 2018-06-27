# import ptvsd
import fmrest
from fmrest.exceptions import FileMakerError
import time
from datetime import datetime
import atexit
import os
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import configparser
import multiprocessing
from multiprocessing import Process
from omxplayer.player import OMXPlayer

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


def play_voice():
    player = OMXPlayer('play.mp3')
    player.set_volume(400)
    time.sleep(player.duration() + 1)

# make the connection to the FMS Data API
fms = fmrest.Server(Config.get('FMS', 'url'),
                        user=Config.get('FMS', 'user'),
                        password=Config.get('FMS', 'pw'),
                        database=Config.get('FMS', 'file'),
                        layout=Config.get('FMS', 'layout'))
try:
    token = fms.login()
except Exception:
    # quit right here, no point in continuiing
    print(str( datetime.now()) + ' - Could not log into FileMaker... Stopping.')
    exit()
# print(token)

# hook into the motor hat and configure the two motors
mh = Adafruit_MotorHAT(addr=0x60,freq=70)
mouth = mh.getMotor(MOTOR_MOUTH)
mouth.setSpeed(100)
head =  mh.getMotor(MOTOR_HEAD_TAIL)
head.setSpeed(100)

# while True:
print(str( datetime.now()) + ' - Starting the loop...')

# release both motors
mouth.run(Adafruit_MotorHAT.RELEASE)
head.run(Adafruit_MotorHAT.RELEASE)

# find the todo records
find_request = [{'flag_ready': '1'}]
try:
    foundset = fms.find(query=find_request)
except FileMakerError:
    if fms.last_error == 401:
        print(str( datetime.now()) + ' - Nothing found for now...')
        # break and continue the loop
        exit()
    else:
        print(fms.last_error)

print(str( datetime.now()) + ' - Record found...')
todo = foundset[0]
old_notes = todo.notes
# print(old_notes)
print(str( datetime.now()) +' - mp3 is at ' + todo.audio_file)

# download the mp3
print(str( datetime.now()) +' - Downloading the mp3...')
name, type_, length, response = fms.fetch_file(todo.audio_file, stream=True)
with open('play.mp3', 'wb') as file_:
    for chunk in response.iter_content(chunk_size=2048): 
        if chunk:
            file_.write(chunk)

voice = Process(target=play_voice)
print(str( datetime.now()) + ' - Start the playback')
voice.start()

# move the mouth in sync with the speech
for x in range(0,4):
    print(str( datetime.now()) + ' - Message during playback')
    # move the mouth
    # mouth.run(Adafruit_MotorHAT.BACKWARD)
    time.sleep(1)
    # mouth.run(Adafruit_MotorHAT.RELEASE)
    # time.sleep(1)



# now update the FM record to mark that it is done
print(str( datetime.now()) + ' - Updating the FM record')
todo['flag_ready'] = ''
todo['notes'] = 'Done - ' + str( datetime.now()) + '\n' + old_notes
fms.edit(todo)
print(str( datetime.now()) + ' - FM record updated')
