import simpleaudio as sa
from time import sleep

# wave_obj = sa.WaveObject.from_wave_file("woop_2001_SO_S16_LE_48k.wav")
wave_obj = sa.WaveObject.from_wave_file("radar_edit.wav")
play_obj = wave_obj.play()
#play_obj.wait_done() #blocking call
while True:
    if(play_obj.is_playing()):
        print('Playing')
        sleep(0.5)
    else:
        print('Ended')
        break

