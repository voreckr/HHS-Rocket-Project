import message
import sys
"""
R. Voreck 4/18/18

This script can be used to reprogram the GP-20U7 GPS module permanently to :
- eliminante all message types except GPGGA
- set baud rate from default (9600) to 4800
- permanently save all new setting in flash on GPS unit: affects future power up state.

"""

OLDBAUD = 9600
NEWBAUD = 4800

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
print "Setting NAV5 config to airborne mode..."

Apparently, this adjusts the navigaion input filters, and manual advises agains adjusting these:
..."The navigation input filters in CFG-NAV5 mask the input data of the navigation engine
These settings are already optimized. Do not change any parameters unless advised by u-blox
support engineers."

navconfig = message.UBXMessage('CFG-NAV5', "\x01\x00\x07\x03\x00\x00\x00\x00\x10'\x00\x00\x05\x00\xfa\x00\xfa\x00d\x00,\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
(ack, null) = message.send(navconfig, baudrate=OLDBAUD)
if ack:
    print "ACK: ", ack.emit()
else:
    print "Didn't get ACK."
	
	
Default message type list:
$GPGGA - keep
$GPGLL - delete
$GPGSA - delete
$GPGSV - delete
$GPRMC - delete
$GPVTG - delete

"""
reprogram_msgs = False
if reprogram_msgs:
	print "\nSetting GLL message rate to 0.."
	glloff = message.NMEA_SetRateMsg('GLL', 0)
	# print dump(glloff.emit())
	# 0000   24 50 55 42 58 2C 34 30    $PUBX,40
	# 0008   2C 47 4C 4C 2C 30 2C 30    ,GLL,0,0
	# 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
	# 0018   2A 35 43 0D 0A             *5C..
	message.send(glloff, baudrate=OLDBAUD)
	print "Done." # NMEA messages don't get ACK'd

if reprogram_msgs:
	print "\nSetting GSA message rate to 0.."
	gsaoff = message.NMEA_SetRateMsg('GSA', 0)
	# print dump(gsaoff.emit())
	# Setting GSA message rate to 0..
	# 0000   24 50 55 42 58 2C 34 30    $PUBX,40
	# 0008   2C 47 53 41 2C 30 2C 30    ,GSA,0,0
	# 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
	# 0018   2A 34 45 0D 0A             *4E..
	message.send(gsaoff, baudrate=OLDBAUD)
	print "Done." # NMEA messages don't get ACK'd

if reprogram_msgs:
	print "\nSetting GSV message rate to 0.."
	gsvoff = message.NMEA_SetRateMsg('GSV', 0)
	# print dump(gsvoff.emit())
	# Setting GSV message rate to 0..
	# 0000   24 50 55 42 58 2C 34 30    $PUBX,40
	# 0008   2C 47 53 56 2C 30 2C 30    ,GSV,0,0
	# 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
	# 0018   2A 35 39 0D 0A             *59..	
	message.send(gsvoff, baudrate=OLDBAUD)
	print "Done." # NMEA messages don't get ACK'd

if reprogram_msgs:
	print "\nSetting RMC message rate to 0.."
	rmcoff = message.NMEA_SetRateMsg('RMC', 0)
	# print dump(rmcoff.emit())
	# Setting RMC message rate to 0..
	# 0000   24 50 55 42 58 2C 34 30    $PUBX,40
	# 0008   2C 52 4D 43 2C 30 2C 30    ,RMC,0,0
	# 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
	# 0018   2A 34 37 0D 0A             *47..

	message.send(rmcoff, baudrate=OLDBAUD)
	print "Done." # NMEA messages don't get ACK'd

if reprogram_msgs:
	print "\nSetting VTG message rate to 0.."
	vtgoff = message.NMEA_SetRateMsg('VTG', 0)
	# print dump(vtgoff.emit())
	# Setting VTG message rate to 0..
	# 0000   24 50 55 42 58 2C 34 30    $PUBX,40
	# 0008   2C 56 54 47 2C 30 2C 30    ,VTG,0,0
	# 0010   2C 30 2C 30 2C 30 2C 30    ,0,0,0,0
	# 0018   2A 35 45 0D 0A             *5E..

	message.send(vtgoff, baudrate=OLDBAUD)
	print "Done." # NMEA messages don't get ACK'd	
	
chg_baud = True
if chg_baud:
	print "\nSetting NEWBAUD rate to %d..." % NEWBAUD
	print "Port 1"
	setbaudmsg = message.NMEA_SetBaudMessage(1, NEWBAUD)
	# print dump(setbaudmsg.emit())
	# Setting NEWBAUD rate to 4800...
	# Port 1
	# 0000   24 50 55 42 58 2C 34 31    $PUBX,41
	# 0008   2C 31 2C 37 2C 33 2C 34    ,1,7,3,4
	# 0010   38 30 30 2C 30 2A 31 33    800,0*13
	# 0018   0D 0A                      ..
	message.send(setbaudmsg, OLDBAUD)

if chg_baud:
	print "Port 2"
	setbaudmsg = message.NMEA_SetBaudMessage(2, NEWBAUD)
	message.send(setbaudmsg, baudrate=OLDBAUD)
	print "Done."

	print "\nSaving settings to flash..."
	(ack, null) = message.send(message.UBXSaveConfig(), OLDBAUD)
	(ack, null) = message.send(message.UBXSaveConfig(), NEWBAUD)
	if ack:
		print "ACK: ", dump(ack.emit())
	else:
		print "Didn't get ACK."

sys.exit()
    
print "Verifying NAV settings..."
(settings, ack) = message.send(message.UBXPollNav5(), NEWBAUD)
print "New settings: ", settings.payload
