#!/usr/bin/env python

import time
import serial
# import io

# hex dump routine used for debugging
FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])

def dump(src, length=8):
    N=0; result=''
    while src:
       s,src = src[:length],src[length:]
       hexa = ' '.join(["%02X"%ord(x) for x in s])
       s = s.translate(FILTER)
       result += "%04X   %-*s   %s\n" % (N, length*3, hexa, s)
       N+=length
    return result


"""
ser = serial.Serial(
	port='COM3',
	baudrate = 9600,
	parity=serial.PARITY_NONE,
	stopbits=serial.STOPBITS_ONE,
	bytesize=serial.EIGHTBITS,
	timeout=2
)
"""

import serial.tools.list_ports as port_list
ports = list(port_list.comports())
for p in ports:
    print (p)

counter=0
try:
  ser = serial.Serial('COM3')
except serial.serialutil.SerialException:
  ser.close()
  ser = serial.Serial('COM3')
  
while 1:
	ser_text = ser.readline().decode('ascii').rstrip()
	# ser_text = io.TextIOWrapper(ser, newline='\r')
	# ser_text.readline()
	outline = str(counter) + ': ' + str( ser_text )
	print (outline)
	# print (dump(str(ser_text)))
	counter += 1

