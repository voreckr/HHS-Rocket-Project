#!/bin/bash
cd /home/pi
echo "" >> ~/nohup.out
echo "##################################" >> ~/nohup.out
date >> ~/nohup.out
nohup python3 /home/pi/HHS/RF\ Link\ related/XBee\ Modules/ADC_Transmit_HHS_6A.py &

