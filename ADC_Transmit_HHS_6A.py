# Copyright 2017, Digi International Inc.
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from digi.xbee.devices import XBeeDevice
from digi.xbee.io import IOLine, IOMode
import threading
from threading import Thread
import time
import datetime
from time import sleep
from datetime import timedelta
from datetime import datetime
from pytimeparse.timeparse import timeparse
import struct
from digi.xbee.models.options import TransmitOptions
import serial
import message
import sys
import signal
import os
import board
import busio
import adafruit_bmp280
import adafruit_mma8451
import subprocess

# Updated to send_data_64 R Voreck 10/29/18
# 11/12/18 RWV - Added Transmit Options Disable ACK
# 5/4/19 RWV & ZY - Renable ACK and handled exceptions
# 6/1/19 RWV - Fixed some GPS bugs
# 6/2/19 RWV - Added GPS UBLOX Setup
# 6/15/19 RWV - Added headless support & signal handling
# 1/26/20 RWV GPS Timeset
# 2/16/20 RWV Rev 6A Copy from Zach, then bug fix
version = "Rev 6A 2/16/20"

################## Initialization ##########################################
#
#

# TODO: Replace with the serial port where your local module is connected to. 
PORT = "/dev/XB0"
# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 9600

DATA_TO_SEND = "Hello XBee!"
REMOTE_NODE_ID = "XBEE_A"


#GPS
GPS_str = " "
ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=2
)

#I2C port
i2c = busio.I2C(board.SCL, board.SDA)

#BMP 280
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

#sea level is actually ground level
bmp280.sea_level_pressure = bmp280.pressure
Alt = 0
Temp = 0
Pressure = 0

#Accelerometer
#accelerometer
sensor = adafruit_mma8451.MMA8451(i2c)
accx = 0
accy = 0
accz = 0


#Camera
#camera = PiCamera()

#ADC 
# Initialize Globals here
IOLINE_IN = IOLine.DIO3_AD3 
OLDBAUD = 9600   # GPS Serial Port Baud Rate 
LOGFILE = ""
stop_requested = False
#time and date
locDate = ""
locTime = ""
TimeOK = False


###################### subroutine definition ###############
#
#
#
def log(caption):
    global LOGFILE
    now = datetime.now()
    now_str = datetime.strftime(now, "%a %Y-%m-%d %H:%M:%S")
    LOGFILE.write( now_str + ": " + caption + "\r\n" )
    LOGFILE.flush()

def sig_handler(signum, frame):
    log("handling signal: %s" % signum)

    global stop_requested
    stop_requested = True    

def printtime(mytime, caption):
    strings = mytime.strftime("%Y,%m,%d,%H,%M,%S")
    # t = strings.split(',')
    # numbers = [ int(x) for x in t ]
    now = datetime.now()
    now_str = datetime.strftime(now, "%a %Y-%m-%d %H:%M")

    log ( caption + strings )

def parse_time():  # avail_time in minutes
    atfs = open(sample_file,"r")
    avail_time_str = atfs.readline()
    end_time_str = end_time_str.rstrip()
    atd = int(timeparse(avail_time_str)/60) # returned in minutes
    end_time1 = datetime.strptime(end_time_str,"%Y-%m-%d %H:%M:%S")
    return atd, end_time1, on_off, why

def setTime(localTime):
    setResp = subprocess.getoutput("sudo date -u -s" + localTime)
    log("setTime response = " +setResp)
                    
def setDate(locDate):
    dateResp = subprocess.getoutput("sudo date -u -s" + locDate)

def GPS_Setup():
    """    
    GPS Receiver UBLOX GPS Chip reporgramming setup:
    copied from setup_ublox2.py 6/2/19
    Default message type list:
    $GPGGA - keep
    $GPGLL - delete
    $GPGSA - delete
    $GPGSV - delete
    $GPRMC - keep
    $GPVTG - delete
    """
    reprogram_msgs = True
    if reprogram_msgs:
        log ("GPS Setup: GLL message rate to 0..")
        glloff = message.NMEA_SetRateMsg('GLL', 0)
        # log dump(glloff.emit())
        # 0000   24 50 55 42 58 2C 34 30    $PUBX,40
        # 0008   2C 47 4C 4C 2C 30 2C 30    ,GLL,0,0
        # 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
        # 0018   2A 35 43 0D 0A             *5C..
        message.send(glloff, baudrate=OLDBAUD)
        log ("Done.") # NMEA messages don't get ACK'd

    if reprogram_msgs:
        log ("GPS Setup: GSA message rate to 0..")
        gsaoff = message.NMEA_SetRateMsg('GSA', 0)
        # log dump(gsaoff.emit())
        # Setting GSA message rate to 0..
        # 0000   24 50 55 42 58 2C 34 30    $PUBX,40
        # 0008   2C 47 53 41 2C 30 2C 30    ,GSA,0,0
        # 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
        # 0018   2A 34 45 0D 0A             *4E..
        message.send(gsaoff, baudrate=OLDBAUD)
        log ("Done.") # NMEA messages don't get ACK'd

    if reprogram_msgs:
        log ("GPS Setup: GSV message rate to 0..")
        gsvoff = message.NMEA_SetRateMsg('GSV', 0)
        # log dump(gsvoff.emit())
        # Setting GSV message rate to 0..
        # 0000   24 50 55 42 58 2C 34 30    $PUBX,40
        # 0008   2C 47 53 56 2C 30 2C 30    ,GSV,0,0
        # 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
        # 0018   2A 35 39 0D 0A             *59..	
        message.send(gsvoff, baudrate=OLDBAUD)
        log ("Done.") # NMEA messages don't get ACK'd

    """if reprogram_msgs:
        log ("GPS Setup: RMC message rate to 0..")
        rmcoff = message.NMEA_SetRateMsg('RMC', 0)
        # log dump(rmcoff.emit())
        # Setting RMC message rate to 0..
        # 0000   24 50 55 42 58 2C 34 30    $PUBX,40
        # 0008   2C 52 4D 43 2C 30 2C 30    ,RMC,0,0
        # 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
        # 0018   2A 34 37 0D 0A             *47..
        message.send(rmcoff, baudrate=OLDBAUD)
        log ("Done.") # NMEA messages don't get ACK'd"""

    if reprogram_msgs:
        log ("GPS Setup: VTG message rate to 0..")
        vtgoff = message.NMEA_SetRateMsg('VTG', 0)
        # log dump(vtgoff.emit())
        # Setting VTG message rate to 0..
        # 0000   24 50 55 42 58 2C 34 30    $PUBX,40
        # 0008   2C 56 54 47 2C 30 2C 30    ,VTG,0,0
        # 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
        # 0018   2A 35 45 0D 0A             *5E..
        message.send(vtgoff, baudrate=OLDBAUD)
        
        log ("GPS Setup: All Done.\n") # NMEA messages don't get ACK'd	

########################## main program ############################
#
#

def main_loop():
    global ser
    global stop_requested

    ver_str = " " + version + " "*(43-len(version)-1)    
    log(" +-------------------------------------------+")
    log(" | XBee Python Library Read Local ADC Sample |")
    log(" | Send_data_64,W/ACK, W/GPS & UBLOX 7 setup |")
    log(" | Headless/Sig, GPS Timeset                 |")
    log(" |" + ver_str +                             "|")
    log(" +-------------------------------------------+\n")
    log("Date, MQ-4 (V), connection, Latitude, Longitude, altitude (m), Temperature (C), Pressure (hPa), acceleration x m/s^2, acceleration y m/s^2, acceleration z m/s^2")
    GPS_Setup() # Initialize GPS so only GPGGA messages are sent
    th = None
    device = XBeeDevice(PORT, BAUD_RATE)

    try:    
        device.open()
        device.set_sync_ops_timeout(60) # allow time to get back in range
        
        stop_requested = False

        # Obtain the remote XBee device from the XBee network.
        xbee_network = device.get_network()
        remote_device = xbee_network.discover_device(REMOTE_NODE_ID)
        remote_64addr = remote_device.get_64bit_addr()
        if remote_device is None:
            log("Could not find the remote device")
            exit(1)
        log ("Waiting 10 Sec for XBee Pairing to complete...")
        time.sleep(10)
        log("Configured to send to device %s ..." % (remote_64addr))
        
        device.set_io_configuration(IOLINE_IN, IOMode.ADC)
        
        def polling_GPS():
            global stop_requested
            global ser
            global locTime
            global locDate
            while not stop_requested:
                x = ser.readline()
                global GPS_str
                
                # GPS_str = x.decode()
                temp = x.decode()
                # 0      1         2          3 4           5 6 7  8    9     10 11   12 14  
                # $GPGGA,044928.00,3724.86080,N,12211.54879,W,1,05,2.27,-18.9,M,-30.1,M,,*7F
                GPSlist = temp.split(',')
                # GPSlist[2]='3724.86080'
                #             DDMM.MMMMM
                #             0123456789
                # GPSlist[4]='12211.54879'
                # locTime = "" # NOT THE RIGHT PLACE to clear these globals
                # locDate = ""
                if (len(GPSlist)>1):
                    if(GPSlist[0] == "$GPGGA"):
                        if (len(GPSlist[2])>8 and len(GPSlist[4])>10):
                            lat_str = "%10.7f" % (float(GPSlist[2][0:2])+float(GPSlist[2][2:10])/60)
                            lon_str = "%12.7f" % (-1*(float(GPSlist[4][0:3])+float(GPSlist[4][3:11])/60))
                            GPS_str = lat_str +', '+lon_str
                        else:
                            GPS_str = ''
                    elif(GPSlist[0] == "$GPRMC"):
                    # 0      1      2 3        4 5         6 7     8     9      10    11
                    # $GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4, 0320,003.1,W*6A
                        #date
                        day = GPSlist[9][0:2]
                        month = GPSlist[9][2:4]
                        year = "20" + GPSlist[9][4:]
                        locDate = year+"-"+month+"-"+day
                        #time
                        hours = GPSlist[1][0:2]
                        minutes = GPSlist[1][2:4]
                        seconds = GPSlist[1][4:]
                        locTime = hours+":"+minutes+":"+seconds
                        # log("GPS local time is: " + locTime + "local date is " + locDate+"\n")
                        
                else:
                    GPS_str = ''
                # log (GPS_str)
                time.sleep(0.5)
        
        def polling_BMP():
            global Alt
            global Temp
            global Pressure
            while not stop_requested:
                Alt = bmp280.altitude
                Temp = bmp280.temperature
                Pressure = bmp280.pressure
                time.sleep(1.0)
        
        def accelerometer():
            global accx
            global accy
            global accz
            while not stop_requested:
                Acceleration = sensor.acceleration
                accx = Acceleration[0]
                accy = Acceleration[1]
                accz = Acceleration[2]
                orientation = sensor.orientation
                time.sleep(1.0)
        
        '''def mycamera(signal):
            global camera
            if signal:
                camera.start_recording('/home/pi/video.h264')
            else:
                camera.stop_recording()
        
        def camera_manager():
            camera_counter = -1000
            #on launch pad
            
            #lift off
            if (Alt > 3):
                #sets camera counter
                camera_counter = 0
                mycamera(True)
            
            while Alt < 10:
                camera_counter += 1
                time.sleep(10)
            #on ground for 30 seconds
            
            if (camera_counter > 3):
                mycamera(False)
        '''
        def polling_adc():
            global stop_requested
            global GPS_str
            global Alt
            global Temp
            global Pressure
            global accx
            global accy
            global accz
            D3 = "" 
            log (str(IOLINE_IN))
            while not stop_requested:
                #Variables
                Alt_str = "%0.2f" % Alt
                Temp_str = "%0.2f" % Temp
                Press_str = "%0.3f" % Pressure
                accx_str = "%0.2f" % accx
                accy_str = "%0.2f" % accy
                accz_str = "%0.2f" % accz
                # Read the analog value from the input line.
                value = device.get_adc_value(IOLINE_IN)
                now = datetime.now()
                time.sleep(0.1)
                
                now_str = datetime.strftime(now, "%m/%d, %H:%M:%S")
                old_now = now
                Gas = "%5.3f" % (value/1024*3.4)
                D1 = now_str + ", " + Gas + D3 + ', ' + GPS_str
                # D1 = now_str + " " + D1 + D3 
                data_len = len(D1)
                D2 = "Sent %d bytes to %s >> %s" % (data_len, REMOTE_NODE_ID, D1)
                # log("%s: %d" % (IOLINE_IN, value))
                # log("Sending data to %s >> %s..." % (remote_64addr, DATA_TO_SEND))
                #Format ("Date, MQ-4 (V), connection, Latitude, Longitude, altitude (m), Temperature (C), Pressure (hPa), acceleration x m/s^2, acceleration y m/s^2, acceleration z m/s^2 ")
                data = [now_str, Gas, D3, GPS_str, Alt_str, Temp_str, Press_str, accx_str, accy_str, accz_str]
                record = ", ".join(data)
                log(record)
                #print("Altitude = " + Alt_str + "meters")
                # device.send_data(remote_device, D1)
                # device._send_data_64(remote_64addr, D1, TransmitOptions.DISABLE_ACK.value) # we already have the 64 bit address, so dont get it again
                try:
                    device._send_data_64(remote_64addr, D1) # Enable ACK, we already have the 64 bit address, so dont get it again
                    RawRssi = device.get_parameter("DB") 
                    Rssi = -1 * struct.unpack("=B", RawRssi )[0]
                    D3 = " %4.0f dBm" % Rssi 
                except:
                    log("Route not found")
                    D3 = " -999 dBm"
                # device.send_data(remote_device, D1)
                # log("Success")
                # time.sleep(20) # Works!!
                time.sleep(0.1)
        
        def locTimeSetter():
            global TimeOK
            global locTime
            global locDate
            time.sleep(20.0)
            while not TimeOK:
                NTPStatus = subprocess.getoutput("timedatectl | grep synchronized | sed -e 's/.*: //'")
                # log("NTPStatus="+NTPStatus)
                if(not(NTPStatus == "yes")):
                    if(len(locTime) > 1 and len(locDate) > 1):
                        log("NTP not avail, setting time and date to GPS:\n\ttime: " + locTime + " date: " + locDate)
                        log("locTime:"+locTime)
                        time.sleep(1.0)
                        setDate(locDate)
                        time.sleep(1.0)
                        setTime(locTime)
                        TimeOK = True
                    else:
                        log("GPS Time and NTP are not working: time stamp is wrong")
                else:
                    log("NTP Time is in use.")
                    TimeOK = True
                time.sleep(60.0)
        
        th = threading.Thread(target=polling_adc)
        th.start()
        th2 = threading.Thread(target=polling_GPS)
        th2.start()
        th3 = threading.Thread(target=polling_BMP)
        th3.start()
        th4 = threading.Thread(target=locTimeSetter)
        th4.start()
        th5 = threading.Thread(target=accelerometer)
        th5.start()
        while not stop_requested:
            time.sleep(2)

    finally:
        stop_requested = True
        if th is not None and th.isAlive():
            th.join()
        if th2 is not None and th2.isAlive():
            th2.join()
        if th3 is not None and th3.isAlive():
            th3.join()
        if th5 is not None and th5.isAlive():
            th5.join()
        """if th4 is not None and th4.isAlive():
            th4.join()
            camera.stop_recording()"""
        if device is not None and device.is_open():
            device.close()
        # if ser is not None: 
            # if ser.is_open():  
                # ser.close()
#        gives error 6/15/19:
        # File "ADC_Transmit_HHS_5.py", line 291, in main_loop
        # if ser.is_open():
        # TypeError: 'bool' object is not callable

 
def main():
    global LOGFILE
    global stop_requested
    
    logfile_name = "/home/pi/HHS_logfile.txt"
    LOGFILE = open(logfile_name, "a+")

    mypid = os.getpid()
    pidfile_name = "/home/pi/HHS_pidfile.txt"
    PIDFILE = open(pidfile_name, "w+")
    PIDFILE.write(  str(mypid) + "\n" )
    PIDFILE.flush()

    stop_requested = False 
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    
    t = Thread(target=main_loop)
    t.start()
    t.join()
    log("main_loop join and task completed\n")
    LOGFILE.close()
    
    

if __name__ == '__main__':
    main()