import fmrest
from fmrest.exceptions import FileMakerError
import time
from datetime import datetime
from datetime import timedelta
import atexit
import os
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import configparser
import multiprocessing
from multiprocessing import Process
from omxplayer.player import OMXPlayer
import json

MOTOR_HEAD_TAIL = 1
MOTOR_MOUTH = 2

# get the config file
myfile = __file__
mydir = os.path.dirname(myfile)
Config = configparser.ConfigParser()
Config.read(os.path.join(mydir, 'billy.ini'))

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
def head_tilt(how_many_seconds):
    print(str( datetime.now()) + ' - sub-process head movement for ' + str(how_many_seconds))
    head.setSpeed(fish_head_speed)
    head.run(Adafruit_MotorHAT.BACKWARD)
    # set to forward to move the tail
    time.sleep(int(how_many_seconds))
    head.run(Adafruit_MotorHAT.RELEASE)
    if fish_waggle_tail == True:
        waggle_tail()
    print(str( datetime.now()) + ' - sub-process head movement done')

# function to waggle the tail
def waggle_tail():
     # set to forward to move the tail
    for x in range(3):
        print(str( datetime.now()) + ' - sub-process tail iteration ' + str(x))
        head.run(Adafruit_MotorHAT.FORWARD)
        time.sleep(0.15)
        head.run(Adafruit_MotorHAT.RELEASE)
        time.sleep(0.20)

def mouth_open(how_many_seconds, how_wide):
    print(str( datetime.now()) + ' - sub-process mouth movement for ' + str(how_many_seconds) + ' seconds')
    if how_wide == 'full':
        speed = fish_mouth_speed
    elif how_wide == 'half':
        speed = fish_mouth_speed / 2
    mouth.setSpeed(speed)
    mouth.run(Adafruit_MotorHAT.BACKWARD)
    time.sleep(float(how_many_seconds)/1000.0)
    mouth.run(Adafruit_MotorHAT.RELEASE)
    print(str( datetime.now()) + ' - sub-process mouth movement done')

def play_voice():
    player = OMXPlayer('play.mp3')
    player.set_volume(100)
    time.sleep(player.duration() + 1)

def get_file(response):
    print(str( datetime.now()) + ' - sub-process download started.')
    with open('play.mp3', 'wb') as file_:
        for chunk in response.iter_content(chunk_size=2048): 
            if chunk:
                file_.write(chunk)
    print(str( datetime.now()) + ' - sub-process download done.')

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

# get the fish config settings
fish = Config['BILLY']
fish_frequency = fish.getint('frequency')
fish_head_speed = fish.getint('head_speed')
fish_mouth_speed = fish.getint('mouth_speed')
fish_waggle_tail = fish.getboolean('waggle_the_tail')
print(str( datetime.now()) + ' - Fish config settings: ' + str(fish_frequency) + '/' + str(fish_head_speed) + '/' + str(fish_mouth_speed) + '/' + str(fish_waggle_tail))

# list of visemes for vowels
vowels_mid = ['@', 'o', 'e' ]
vowels_open = ['a', 'O', 'E' ]
vowels_close = ['i', 'u']
consonants = ['p', 't', 'S', 'f', 'k', 'r']

# hook into the motor hat and configure the two motors
mh = Adafruit_MotorHAT(addr=0x60,freq=70)
mouth = mh.getMotor(MOTOR_MOUTH)
mouth.setSpeed(fish_mouth_speed)
head =  mh.getMotor(MOTOR_HEAD_TAIL)
head.setSpeed(fish_head_speed)

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
        print(str( datetime.now()) + ' ----------------------------------------------------------------------')
        # break and continue the loop
        exit()
    else:
        print(fms.last_error)

print(str( datetime.now()) + ' - Record found...')
todo = foundset[0]
old_notes = todo.notes
# print(old_notes)
print(str( datetime.now()) +' - mp3 is at ' + todo.audio_file)

# prep the download process for the mp3
name, type_, length, response = fms.fetch_file(todo.audio_file, stream=True)
dl = Process(target=get_file, args=(response,))


# turn billy's head here
hhmmss =  todo.duration
[hours, minutes, seconds] = [int(x) for x in hhmmss.split(':')]
x = timedelta(hours=hours, minutes=minutes, seconds=seconds)
duration_from_fm = x.seconds
print(str( datetime.now()) +' - mp3 duration from FM = ' + str(duration_from_fm) + ' seconds')
head_process = Process(target=head_tilt, args=(duration_from_fm,))
print(str( datetime.now()) +' - Turning the head...')
head_process.start()
print(str( datetime.now()) +' - Downloading the mp3...')
dl.start()

#for x in range(0,4):
#    print(str( datetime.now()) + ' - Message during download')
#    time.sleep(1)

# while file is downloading, process the visemes
# keep only those that move the mouth
# start at each word should close the mouth
viseme_list = todo.audio_extra_info


# --> how to determine amount of openess of the mouth?
# percentage perhaps?  so that we can set the frequency? speed?


# create empty list
action_list = []
action_found = False
for line in viseme_list.splitlines():
    # print(str( datetime.now()) + ' ' + line)
    json_line = json.loads(line)
    # time, type and value
    when = json_line['time']
    what = json_line['type']
    vis = json_line['value']

    # we are only going to look at vowels for now
    # but need to record when the next one kicks in so that we have a duration

    if action_found == True:
        when_end = when
        # add the action tuple to the list
        action_list.append((action, when_start, when_end))

    action_found = False
    if vis == 'sil':
        action = 'close'
        action_found = True
    elif vis in vowels_close:
         action = 'close'
         action_found = True
    elif vis in vowels_open:
        action = 'full'
        action_found = True
    elif vis in vowels_mid:
        action = 'half'
        action_found = True
    elif vis in consonants:
        action = 'full'
        action_found = True

    if action_found == True:
        when_start = when
print(str( datetime.now()) + ' - Done parsing the visemes')

# make sure we wait for the download to finish
dl.join()
print(str( datetime.now()) + ' - Done downloading the mp3')

# now play the audio and do the magic
offset = 250 # milliseconds
voice = Process(target=play_voice)
print(str( datetime.now()) + ' - Start the mp3 playback')
start_time = datetime.now() + timedelta(milliseconds=offset)
print(str( datetime.now()) + ' - Start marker time = ' + str(start_time))
voice.start()

print(str( datetime.now()) + ' - Start the motor action')
# move the mouth in sync with the speech
for action_tuple in action_list:
    print(str( datetime.now()) + ' - action: ' + str(action_tuple))
    
    # break down the tuple
    action, when_start, when_end = action_tuple

    # how long does this action take?
    elapsed_time = int(when_end) - int(when_start)
    action_time = start_time + timedelta(milliseconds=int(when_start))
    print(str( datetime.now()) + ' - action length: ' + str(elapsed_time) + ' milliseconds, start target = ' + str(action_time))
    duration_in_seconds = float(elapsed_time) / 1000.0

    # loop and wait until it is our turn
    sleep_time = 2.0 / 1000.0  # to make it seconds
    
    # print(str( datetime.now()) + ' - waiting for: ' + str(action_time))
    while  datetime.now() < action_time:
        # sleep until the time comes for this action
        time.sleep(sleep_time)
    # the time has come, we can now process the action
    print(str( datetime.now()) + ' - the time has come for the action')
    if action == 'close':
        # release the motor
        print(str( datetime.now()) + ' - closing mouth')
        mouth.run(Adafruit_MotorHAT.RELEASE)
        # break
    elif action == 'half':
        # send half power
        mouth_open(duration_in_seconds, action)
        # break
    elif action == 'full':
        # send full power
        mouth_open(duration_in_seconds, action)
        # break

           
print(str( datetime.now()) + ' - Done with the motor action')


# now update the FM record to mark that it is done
print(str( datetime.now()) + ' - Updating the FM record')
todo['flag_ready'] = ''
todo['notes'] = 'Done - ' + str( datetime.now()) + '\n' + old_notes
fms.edit(todo)
print(str( datetime.now()) + ' - FM record updated')
head_process.join()
print(str( datetime.now()) + ' ----------------------------------------------------------------------')
