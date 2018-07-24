import atexit
import configparser
import os
import time
from datetime import datetime, timedelta
from multiprocessing import Process

import fmrest
from Adafruit_MotorHAT import Adafruit_MotorHAT
from fmrest.exceptions import FileMakerError
from omxplayer.player import OMXPlayer

from pydub import AudioSegment

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
    if fish_move_head == False:
        print(str( datetime.now()) + ' - sub-process head movement, head movement not configured') 
    else:
        print(str( datetime.now()) + ' - sub-process head movement for ' + str(how_many_seconds) + ' seconds, motor speed = ' + str(fish_head_speed))
        print(str( datetime.now()) + ' - sub-process head movement, tail waggle = ' + str(fish_waggle_tail)) 
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

def play_voice():
    print(str( datetime.now()) + ' - Delaying the voice playback by ' + str(fish_mouth_wait) + ' milliseconds')
    time.sleep(fish_mouth_wait / 1000.0)
    if app_audio_USB == True:
        print(str( datetime.now()) + ' - playing audio through USB')
        player = OMXPlayer('play.' + audio_type, args=['--adev', 'alsa:plughw:1,0'])
        # to test in terminal: 
        # omxplayer --adev alsa:plughw:1,0 play.MP3
        # 1,0 = card 1, device 0 --> see aplay -l (lowercase L)
    else:
        print(str( datetime.now()) + ' - playing audio through jack')
        player = OMXPlayer('play.' + audio_type)  
    # player.set_volume(app_volume)
    time.sleep(player.duration() + 1)

def get_file():
    print(str( datetime.now()) + ' - sub-process download started.')
    name, type_, length, response = fms.fetch_file(todo.audio_file)
    print(str( datetime.now()) +' - fetched audio file details. name = ' + name + ', type = ' + str(type_) + ', length = ' + str(length) )
    with open('play.' + audio_type, 'wb') as file_:
        file_.write(response.content)
    print(str( datetime.now()) + ' - sub-process download done.')

def determine_pause():
    # wait for a little bit before repeating the loop
    if app_testing_mode == True:
        time.sleep(app_polling_interval_testing / 1000.0)
    else:
        time.sleep(app_polling_interval / 1000.0)

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


# get the app config settings
app_settings = Config['APP']
app_billy = app_settings['use']
app_testing_mode = app_settings.getboolean('testing')
app_polling_interval = app_settings.getint('polling_interval')
app_polling_interval_testing = app_settings.getint('polling_interval_testing')
app_volume = app_settings.getint('volume')
app_audio_amplitude_threshold = app_settings.getint('audio_amplitude_threshold')
app_audio_USB = app_settings.getboolean('audio_use_USB')
# output the settings for inspection
print(str( datetime.now()) + ' - App config settings: '  + app_billy + '/' + 
      str(app_testing_mode) + '/' + 
      str(app_polling_interval) + '/' + 
      str(app_polling_interval_testing))
print(str( datetime.now()) + ' - App audio settings: '  + 
      'amplitude threshold = ' + str(app_audio_amplitude_threshold) + '/' + 
      'use usb audio = ' + str(app_audio_USB))


# get the fish config settings
if app_billy == 'billy1':
    fish = Config['BILLY1']
elif app_billy == 'billy2':
    fish = Config['BILLY2']
fish_frequency = fish.getint('frequency')
fish_head_speed = fish.getint('head_speed')
fish_mouth_speed = fish.getint('mouth_speed')
fish_waggle_tail = fish.getboolean('waggle_the_tail')
fish_move_head = fish.getboolean('move_the_head')
fish_mouth_wait = fish.getint('offset')
fish_mouth_duration = fish.getint('mouth_duration') / 1000.0
# output the settings for inspection
print(str( datetime.now()) + ' - Fish config settings: ' + 
      str(fish_frequency) + '/' + 
      str(fish_head_speed) + '/' + 
      str(fish_mouth_speed) + '/' + 
      str(fish_waggle_tail) + '/' + 
      str(fish_move_head))

# hook into the motor hat and configure the two motors
mh = Adafruit_MotorHAT(addr=0x60,freq=fish_frequency)
mouth = mh.getMotor(MOTOR_MOUTH)
mouth.setSpeed(fish_mouth_speed)
head =  mh.getMotor(MOTOR_HEAD_TAIL)
head.setSpeed(fish_head_speed)

# while True:
print(str( datetime.now()) + ' - Starting the loop...')
while True:

    # release both motors
    mouth.run(Adafruit_MotorHAT.RELEASE)
    head.run(Adafruit_MotorHAT.RELEASE)

    # first try to find if we have a request to just turn the head
    foundset = None
    find_request = None
    find_request = [{'flag_turn_head': '1'}]
    try:
        foundset = fms.find(query=find_request)
        # print(str( datetime.now()) + ' - FMS error = ' + str(fms.last_error))
    except FileMakerError:
        if fms.last_error == 401:
            # no problem, we're going to look for audio to play
            print(str( datetime.now()) + ' - No head turning action requested...')
        else:
            print(str( datetime.now()) +' - Unexpected FMS error: ' + fms.last_error)
            exit()
    else:
        # no error so we found a head-move request
        if foundset is not None:
            todo = foundset[0]
            # override whatever was set in the config file for head movement
            temp_boolean = fish_move_head
            fish_move_head = True
            print(str( datetime.now()) + ' - Head turning action requested...')
            head_process = Process(target=head_tilt, args=(1,))
            print(str( datetime.now()) +' - Turning the head...')
            head_process.start()
            print(str( datetime.now()) + ' - Updating the FM record')
            todo['flag_turn_head'] = ''
            fms.edit(todo)
            # reset the configured head movement
            fish_move_head = temp_boolean
            print(str( datetime.now()) + ' ----------------------------------------------------------------------')
            # continue the loop, we're not going to play any audio
            determine_pause()
            continue

    # find the todo records
    find_request = [{'flag_ready': '1'}]
    try:
        foundset = fms.find(query=find_request)
    except FileMakerError:
        if fms.last_error == 401:
            print(str( datetime.now()) + ' - No speech playback requests found...')
            print(str( datetime.now()) + ' ----------------------------------------------------------------------')
            # continue the loop
            determine_pause()
            continue
        else:
            print(str( datetime.now()) +' - Unexpected FMS error: ' + fms.last_error)
            exit()
 
    # we have something to play
    print(str( datetime.now()) + ' - Record found...')
    todo = foundset[0]
    old_notes = todo.notes
    audio_type = todo.audio_type
    print(str( datetime.now()) +' - audio file (' + audio_type + ') is at ' + todo.audio_file)

    # prep the download process for the mp3
    dl = Process(target=get_file)

    # turn billy's head here
    hhmmss =  todo.duration
    if hhmmss == '':
        duration_from_fm = 2
    else:
        [hours, minutes, seconds] = [int(x) for x in hhmmss.split(':')]
        x = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        duration_from_fm = x.seconds
    print(str( datetime.now()) +' - ' + audio_type + ' duration from FM = ' + str(duration_from_fm) + ' seconds')

    head_process = Process(target=head_tilt, args=(duration_from_fm,))
    print(str( datetime.now()) +' - Turning the head...')
    head_process.start()

    print(str( datetime.now()) +' - Downloading the ' + audio_type + '...')
    dl.start()

    # make sure we wait for the download to finish
    dl.join()
    print(str( datetime.now()) + ' - Done downloading the ' + audio_type)

    # now play the audio and do the magic
    voice = Process(target=play_voice)
    print(str( datetime.now()) + ' - Start the mp3 playback')
    voice.start()

    # decide on mouth movement by amplitude in the audio file frames
    sound = AudioSegment.from_mp3("play.MP3")
    
    """
    # document the sound, informational purposes only
    # get the frame rate
    sample_rate = sound.frame_rate
    # get amount of bytes contained in one sample
    sample_size = sound.sample_width
    # get channels
    channels = sound.channels
    print(str( datetime.now()) + ' - sample rate = ' + str(sample_rate))
    print(str( datetime.now()) + ' - sample size (bytes) = ' + str(sample_size))
    print(str( datetime.now()) + ' - channels = ' + str(channels))
    print(str( datetime.now()) + ' - length in seconds = ' + str(sound.duration_seconds))
    """

    # going to iterate over the mp3 file in millisecond chunks
    chunk_duration = 200
    chunks = sound[::chunk_duration]
    for chunk in chunks:
        amplitude = chunk.max
        if amplitude > app_audio_amplitude_threshold:
            # open and close the mouth if the sound is over our amplitude threshold
            # print(str( datetime.now()) + ' - max amplitude = ' + str(amplitude))
            mouth.run(Adafruit_MotorHAT.BACKWARD)
            time.sleep(fish_mouth_duration)
            mouth.run(Adafruit_MotorHAT.RELEASE)
            # print(str( datetime.now()) + ' - mouth code done' )
            time_allow_for_spent = 15 # based on checking the difference in the timestamps
            time.sleep((chunk_duration - fish_mouth_duration - time_allow_for_spent) / 1000.0)
        else:
            mouth.run(Adafruit_MotorHAT.RELEASE)   
            time.sleep(chunk_duration / 1000.0)
 
    voice.join()

    print(str( datetime.now()) + ' - Done with the audio playback')

    # now update the FM record to mark that it is done
    print(str( datetime.now()) + ' - Updating the FM record')
    todo['flag_ready'] = ''
    todo['notes'] = 'Done - ' + str( datetime.now()) + '\n' + old_notes
    fms.edit(todo)
    print(str( datetime.now()) + ' - FM record updated')
    head_process.join()
    print(str( datetime.now()) + ' ----------------------------------------------------------------------')
    # pause for a bit
    determine_pause()
