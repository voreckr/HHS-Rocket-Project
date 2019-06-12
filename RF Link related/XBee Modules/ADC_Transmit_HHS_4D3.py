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

# Updated to send_data_64 R Voreck 10/29/18
# 11/12/18 RWV - Added Transmit Options Disable ACK
# 5/4/19 RWV & ZY - Renable ACK and handled exceptions
# 6/1/19 RWV - Fixed some GPS bugs
# 6/2/19 RWV - Added GPS UBLOX Setup



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

IOLINE_IN = IOLine.DIO2_AD2
OLDBAUD = 9600   # GPS Serial Port Baud Rate 

###################### subroutine definition ###############
#
#
#

def printtime(mytime, caption):
    strings = mytime.strftime("%Y,%m,%d,%H,%M,%S")
    # t = strings.split(',')
    # numbers = [ int(x) for x in t ]
    now = datetime.now()
    now_str = datetime.strftime(now, "%a %Y-%m-%d %H:%M")

    print ( caption + strings )

def parse_time():  # avail_time in minutes
    atfs = open(sample_file,"r")
    avail_time_str = atfs.readline()
    end_time_str = end_time_str.rstrip()
    atd = int(timeparse(avail_time_str)/60) # returned in minutes
    end_time1 = datetime.strptime(end_time_str,"%Y-%m-%d %H:%M:%S")
    return atd, end_time1, on_off, why
    
def GPS_Setup():
    """    
    GPS Receiver UBLOX GPS Chip reporgramming setup:
    copied from setup_ublox2.py 6/2/19
    Default message type list:
    $GPGGA - keep
    $GPGLL - delete
    $GPGSA - delete
    $GPGSV - delete
    $GPRMC - delete
    $GPVTG - delete
    """
    reprogram_msgs = True
    if reprogram_msgs:
        print ("GPS Setup: GLL message rate to 0..")
        glloff = message.NMEA_SetRateMsg('GLL', 0)
        # print dump(glloff.emit())
        # 0000   24 50 55 42 58 2C 34 30    $PUBX,40
        # 0008   2C 47 4C 4C 2C 30 2C 30    ,GLL,0,0
        # 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
        # 0018   2A 35 43 0D 0A             *5C..
        message.send(glloff, baudrate=OLDBAUD)
        print ("Done.") # NMEA messages don't get ACK'd

    if reprogram_msgs:
        print ("GPS Setup: GSA message rate to 0..")
        gsaoff = message.NMEA_SetRateMsg('GSA', 0)
        # print dump(gsaoff.emit())
        # Setting GSA message rate to 0..
        # 0000   24 50 55 42 58 2C 34 30    $PUBX,40
        # 0008   2C 47 53 41 2C 30 2C 30    ,GSA,0,0
        # 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
        # 0018   2A 34 45 0D 0A             *4E..
        message.send(gsaoff, baudrate=OLDBAUD)
        print ("Done.") # NMEA messages don't get ACK'd

    if reprogram_msgs:
        print ("GPS Setup: GSV message rate to 0..")
        gsvoff = message.NMEA_SetRateMsg('GSV', 0)
        # print dump(gsvoff.emit())
        # Setting GSV message rate to 0..
        # 0000   24 50 55 42 58 2C 34 30    $PUBX,40
        # 0008   2C 47 53 56 2C 30 2C 30    ,GSV,0,0
        # 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
        # 0018   2A 35 39 0D 0A             *59..	
        message.send(gsvoff, baudrate=OLDBAUD)
        print ("Done.") # NMEA messages don't get ACK'd

    if reprogram_msgs:
        print ("GPS Setup: RMC message rate to 0..")
        rmcoff = message.NMEA_SetRateMsg('RMC', 0)
        # print dump(rmcoff.emit())
        # Setting RMC message rate to 0..
        # 0000   24 50 55 42 58 2C 34 30    $PUBX,40
        # 0008   2C 52 4D 43 2C 30 2C 30    ,RMC,0,0
        # 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
        # 0018   2A 34 37 0D 0A             *47..
        message.send(rmcoff, baudrate=OLDBAUD)
        print ("Done.") # NMEA messages don't get ACK'd

    if reprogram_msgs:
        print ("GPS Setup: VTG message rate to 0..")
        vtgoff = message.NMEA_SetRateMsg('VTG', 0)
        # print dump(vtgoff.emit())
        # Setting VTG message rate to 0..
        # 0000   24 50 55 42 58 2C 34 30    $PUBX,40
        # 0008   2C 56 54 47 2C 30 2C 30    ,VTG,0,0
        # 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
        # 0018   2A 35 45 0D 0A             *5E..
        message.send(vtgoff, baudrate=OLDBAUD)
        
        print ("GPS Setup: All Done.\n") # NMEA messages don't get ACK'd	

########################## main program ############################
#
#

def main():
    print(" +-------------------------------------------+")
    print(" | XBee Python Library Read Local ADC Sample |")
    print(" | Send_data_64,W/ACK, W/GPS & UBLOX 7 setup |")
    print(" |                           6/9/19 Rev 4D3  |")
    print(" +-------------------------------------------+\n")
    
    GPS_Setup() # Initialize GPS so only GPGGA messages are sent
    
    th = None

    device = XBeeDevice(PORT, BAUD_RATE)

    try:
        device.open()
        device.set_sync_ops_timeout(60) # allow time to get back in range
        
        stop = False

        # Obtain the remote XBee device from the XBee network.
        xbee_network = device.get_network()
        remote_device = xbee_network.discover_device(REMOTE_NODE_ID)
        remote_64addr = remote_device.get_64bit_addr()
        if remote_device is None:
            print("Could not find the remote device")
            exit(1)
        print ("Waiting 10 Sec for XBee Pairing to complete...")
        time.sleep(10)
        print("Configured to send to device %s ..." % (remote_64addr))
        
        device.set_io_configuration(IOLINE_IN, IOMode.ADC)
        
        def polling_GPS():
            while not stop:
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
                if (len(GPSlist)>1):
                    if (len(GPSlist[2])>8 and len(GPSlist[4])>10):
                        lat_str = "%10.7f" % (float(GPSlist[2][0:2])+float(GPSlist[2][2:10])/60)
                        lon_str = "%12.7f" % (-1*(float(GPSlist[4][0:3])+float(GPSlist[4][3:11])/60))
                        GPS_str = lat_str +','+lon_str
                    else:
                        GPS_str = ''
                else:
                    GPS_str = ''
                # print (GPS_str)
                time.sleep(1.0)
                
        def polling_adc():
            global GPS_str
            D3 = "" 
            print (IOLINE_IN)
            while not stop:
                # Read the analog value from the input line.
                value = device.get_adc_value(IOLINE_IN)
                now = datetime.now()
                time.sleep(0.1)
                
                now_str = datetime.strftime(now, "%m/%d %H:%M:%S")
                old_now = now
                D1 = "%5.3f V" % (value/1024*3.4)
                D1 = now_str + " " + D1 + D3 + ',' + GPS_str
                # D1 = now_str + " " + D1 + D3 
                data_len = len(D1)
                D2 = "Sent %d bytes to %s >> %s" % (data_len, REMOTE_NODE_ID, D1)
                # print("%s: %d" % (IOLINE_IN, value))
                # print("Sending data to %s >> %s..." % (remote_64addr, DATA_TO_SEND))
                print(D2)
                # device.send_data(remote_device, D1)
                # device._send_data_64(remote_64addr, D1, TransmitOptions.DISABLE_ACK.value) # we already have the 64 bit address, so dont get it again
                try:
                    device._send_data_64(remote_64addr, D1) # Enable ACK, we already have the 64 bit address, so dont get it again
                    RawRssi = device.get_parameter("DB") 
                    Rssi = -1 * struct.unpack("=B", RawRssi )[0]
                    D3 = " %4.0f dBm" % Rssi 
                except:
                    print("Route not found")
                    D3 = " -999 dBm"
                # device.send_data(remote_device, D1)
                # print("Success")
                # time.sleep(20) # Works!!
                time.sleep(0.1)

        th = threading.Thread(target=polling_adc)
        th.start()
        th2 = threading.Thread(target=polling_GPS)
        th2.start()

        input()

    finally:
        stop = True
        if th is not None and th.isAlive():
            th.join()
        if th2 is not None and th2.isAlive():
            th2.join()
        if device is not None and device.is_open():
            device.close()
        if ser is not None and ser.is_open():
            ser.close()


if __name__ == '__main__':
    main()