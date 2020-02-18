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

# Changes: 
# _3.py 11/10/18 RWV - Added local storage of 64 bit address to avoid need to get it with each message.
# _4.py 11/10/18 RWV - changed to packet receive method to allow additional reception info to be exposed
# _4A.py 2/16/19 RWV - Added OLED diplay of RSS

import array
from digi.xbee.devices import XBeeDevice
from datetime import timedelta
from datetime import datetime
from digi.xbee.packets.base import DictKeys
import os
import re
import signal
from time import sleep

# Globals
# Serial port where local module is connected to
PORT = "/dev/XB0"
# Baud rate of local module.
BAUD_RATE = 9600
stop_requested = False
LOGFILE = ""
version = "Rev 5A 2/16/20"

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

def main():
    device = XBeeDevice(PORT, BAUD_RATE)
    global LOGFILE
    global spinner
    global spinstr
    global stop_requested

    spinner = 0
    spinstr = "|/-\\"
    
    logfile_name = "/home/pi/HHS_logfile.txt"
    LOGFILE = open(logfile_name, "a+")

    mypid = os.getpid()
    pidfile_name = "/home/pi/HHS_pidfile.txt"
    PIDFILE = open(pidfile_name, "w+")
    PIDFILE.write(  str(mypid) + "\n" )
    PIDFILE.flush()
    
    ver_str = " " + version + " "*(41-len(version)-1)       
    log(" +-----------------------------------------+")
    log(" | XBee Python Library Receive Data Sample |")
    log(" | w OLED disp                             |")
    log(" |" + ver_str +                           "|")
    log(" +-----------------------------------------+\n")
    try:
        device.open()
        device.set_sync_ops_timeout(60)
        global D1  
        D1 = ""


        # def data_receive_callback(xbee_message):
            # # print ("got interrupt!")
            # D3 = ""
            # global D1
            # if (len(D1)==0):
                # D1 = str(xbee_message.remote_device.get_64bit_addr())
            
            # D2 = xbee_message.data.decode()
            # # sleep(0.3)
            # # RawRssi = device.get_parameter("DB") 
            # # Rssi = -1 * struct.unpack("=B", RawRssi )[0]
            # # D3 = " %4.0f dBm" % Rssi 
            # # sleep(0.3)

            # print("From %s >> %s %s" % (D1,D2,D3))

        # device.add_data_received_callback(data_receive_callback)

        def packet_received_callback(packet):
            global spinner
            global spinstr
            packet_dict = packet.to_dict()
            # import pdb; pdb.set_trace()
            api_data = packet_dict[DictKeys.FRAME_SPEC_DATA][DictKeys.API_DATA]
            data = api_data[DictKeys.RF_DATA]
            datastr = array.array('B',data).tostring().decode('ascii')
            #  print ("datastr=" + datastr)
            # rssi = api_data[DictKeys.RSSI]
            rssi = -99
            address64 = api_data[DictKeys.X64BIT_ADDR].hex()
            
            # extract and diplay RSSI on OLED display
            p = re.compile(r' ([^ ]*) dBm')
            try:
                last_rssi = p.search(datastr).group(1)
            except AttributeError:
                last_rssi = 0
                log ("Dodged Attribute Error! Possible inability to match dBm search string")
            # print(last_rssi)
            RSSI = int(last_rssi) # convert to number
            file = open("oled.txt","w")  
            # spinner |/-\
            sc = spinstr[spinner % 4]
            spinner += 1
            file.write("RSSI: " + str(RSSI) + " dBm    " + sc + "\n") 
            Xstr =""
            XS = 21 + int((RSSI+30)/4)
            # file.write(str(XS)+"\n") 
            for j in range(1,XS):
                Xstr = Xstr + "*"
            file.write(str(Xstr)+"\n")
            file.close() 

            log("from: {}, RSSI: {}, Data: {}".format(address64, rssi, datastr))

        device.add_packet_received_callback(packet_received_callback)

        stop_requested = False 
        signal.signal(signal.SIGTERM, sig_handler)
        signal.signal(signal.SIGINT, sig_handler)

        log("Waiting for data...\n")
        while(not stop_requested):
            sleep(2)
        
        t = Thread(target=main_loop)
        t.start()
        t.join()
        log("main_loop join and task completed\n")

    finally:
        if device is not None and device.is_open():
            device.close()
    LOGFILE.close()


if __name__ == '__main__':
    main()
