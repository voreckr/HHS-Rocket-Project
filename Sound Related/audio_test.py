import simpleaudio as sa
from time import sleep
import sys
sound_name = sys.argv[1]
print ("working on : ",  sound_name)
# wave_obj = sa.WaveObject.from_wave_file("woop_2001_SO_S16_LE_48k.wav")
wave_obj = sa.WaveObject.from_wave_file(sound_name)
# play_obj = wave_obj.play()
#play_obj.wait_done() #blocking call
while True:
    play_obj = wave_obj.play()
    # play_obj.wait_done() #blocking call
    while True:
        if(play_obj.is_playing()):
            # print('Playing')
            sleep(0.05)
        else:
            print('Ended')
            break

