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

# Updated to send_data_64 R Voreck 10/29/18
# 11/12/18 RWV - Added Transmit Options Disable ACK

# TODO: Replace with the serial port where your local module is connected to. 
PORT = "/dev/XB0"
# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 9600

DATA_TO_SEND = "Hello XBee!"
REMOTE_NODE_ID = "XBEE_A"

IOLINE_IN = IOLine.DIO2_AD2
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


def main():
    print(" +-------------------------------------------+")
    print(" | XBee Python Library Read Local ADC Sample |")
    print(" | Send_data_64 + No ACK   11/12/18  Rev 2   |")
    print(" +-------------------------------------------+\n")

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
        time.sleep(20)
        print("Configured to send to device %s ..." % (remote_64addr))
        
        device.set_io_configuration(IOLINE_IN, IOMode.ADC)
        def polling_adc():
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
                D1 = now_str + " " + D1 + D3
                D2 = "Sending data to %s >> %s" % (REMOTE_NODE_ID, D1)
                # print("%s: %d" % (IOLINE_IN, value))
                # print("Sending data to %s >> %s..." % (remote_64addr, DATA_TO_SEND))
                print(D2)
                device._send_data_64(remote_64addr, D1, TransmitOptions.DISABLE_ACK.value) # we already have the 64 bit addres, so dont get it again
                RawRssi = device.get_parameter("DB") 
                Rssi = -1 * struct.unpack("=B", RawRssi )[0]
                D3 = " %4.0f dBm" % Rssi 
                # device.send_data(remote_device, D1)
                # print("Success")
                # time.sleep(20) # Works!!
                time.sleep(0.1)

        th = threading.Thread(target=polling_adc)
        th.start()

        input()

    finally:
        stop = True
        if th is not None and th.isAlive():
            th.join()
        if device is not None and device.is_open():
            device.close()


if __name__ == '__main__':
    main()
