import simpleaudio as sa
from time import sleep
import sys
sound_name = sys.argv[1]

sounds = [
    "extremely_well.wav",
#    "good_evening_smoothly.wav",
    "human_error.wav",
#    "radar10.wav",
    "radar_edit.wav",
#    "radarLE.wav",
    "radar10A.wav",
    "sorry_daveLE.wav",
    "goodbye.wav",
    "woop_2001_SO_S16_LE_48k.wav",
    "upset.wav",
    "mind_is_going.wav"
    ]
for sound_name in sounds: 
    print ("working on : ",  sound_name)
    # wave_obj = sa.WaveObject.from_wave_file("woop_2001_SO_S16_LE_48k.wav")
    wave_obj = sa.WaveObject.from_wave_file(sound_name)
    # play_obj = wave_obj.play()
    #play_obj.wait_done() #blocking call
#    while True:
    play_obj = wave_obj.play()
    # play_obj.wait_done() #blocking call
    while True:
        if(play_obj.is_playing()):
            # print('Playing')
            sleep(0.05)
        else:
            print('Ended')
            break

