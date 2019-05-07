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

from digi.xbee.devices import XBeeDevice
from time import sleep
from digi.xbee.packets.base import DictKeys
import array
import re


# TODO: Replace with the serial port where your local module is connected to. 
PORT = "/dev/XB0"
# TODO: Replace with the baud rate of your local module.
BAUD_RATE = 9600


def main():
    print(" +-----------------------------------------+")
    print(" | XBee Python Library Receive Data Sample |")
    print(" +-----------------------------------------+\n")

    device = XBeeDevice(PORT, BAUD_RATE)
    global spinner
    global spinstr
    spinner = 0
    spinstr = "|/-\\"
    
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
            # rssi = api_data[DictKeys.RSSI]
            rssi = -99
            address64 = api_data[DictKeys.X64BIT_ADDR].hex()
            
            # extract and diplay RSSI on OLED display
            p = re.compile(r' ([^ ]*) dBm$')
            try:
                last_rssi = p.search(datastr).group(1)
            except AttributeError:
                last_rssi = 0
                print ("Dodged Attribute Error!")
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

            print("from: {}, RSSI: {}, Data: {}".format(address64, rssi, datastr))

        device.add_packet_received_callback(packet_received_callback)

        print("Waiting for data...\n")
        input()

    finally:
        if device is not None and device.is_open():
            device.close()


if __name__ == '__main__':
    main()
