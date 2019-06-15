from threading import Thread
import signal
import time
import sys
from datetime import datetime
LOGFILE = ''

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

def run():
    log("run started")
    while not stop_requested:
        log("running...")
        time.sleep(2)

    log("run exited")


###### main  ################
#
logfile_name = "/home/pi/HHS_logfile.txt"
LOGFILE = open(logfile_name, "a+")

stop_requested = False 
signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGINT, sig_handler)

t = Thread(target=run)
t.start()
t.join()
sys.stdout.write("join completed\n")
sys.stdout.flush()