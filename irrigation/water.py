#!/usr/bin/python3

from datetime import datetime
import time
import RPi.GPIO as GPIO
import argparse
import logging
from systemd.journal import JournalHandler

logger = logging.getLogger("water.py")

def switch(pin):
    GPIO.output(pin,1)
    logging.info(f'pin {pin} is {GPIO.input(pin)} for {time_switch} seconds')
    time.sleep(time_switch)
    GPIO.output(pin,0)
    logging.info(f'turning pin {pin} off, pin state is {GPIO.input(pin)}')

def check_time(start,end,x):
    if start <= x <= end:
        return True
    else:
        return False

def parseArgs():
    parser = argparse.ArgumentParser(description="an utility that checks the time and if it falls within a range turns on a relay for watering the plants")
    parser.add_argument("-s","--start",help="provide the time to start the water, in hours and minutes, i.e. 02:00", default="02:00", required=True)
    parser.add_argument("-e","--end",help="provide the time to stop the water, in hours and minutes, i.e. 03:00",default="03:00", required=True)
    parser.add_argument("-o","--water_open",help="which GPIO pin is the relay to open the water connected to?",default=16,type=int)
    parser.add_argument("-c","--water_close",help="which GPIO pin is the relay to turn off the water connected to?",default=12,type=int)
    parser.add_argument("-u","--humidity",help="which GPIO pin is the humidity sensor connected to?",default=13,required=False,type=int)
    parser.add_argument("-t","--threshold",help="what threshold do you want to set for humidity changes?",default=0.01,required=False,type=float)
    return parser.parse_args()

def logger_setup(logger):
    ###
    # logger to be able to report what is going on directly to journalctl
    ###
    logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s',level=logging.INFO)
    logger.addHandler(JournalHandler())
    #journald_handler = JournalHandler()
    #journald_handler.setFormatter(logging.Formatter(
    #logger.addHandler(journald_handler)
    #logger.setLevel(logging.INFO)


if __name__=="__main__":
    logger_setup(logger) 
    water_status = 1
    time_switch = 60
    #logger = logging.getLogger(__name__)
    args = parseArgs()
    th = args.threshold
    water_open = args.water_open
    water_close = args.water_close
    humidity = args.humidity
    logging.info(f'water will be turned on in the timerange: {args.start} - {args.end}')
    # set up the gpio pins
    GPIO.setmode(GPIO.BOARD) 
    GPIO.setup(water_open, GPIO.OUT)
    GPIO.setup(water_close, GPIO.OUT)
    GPIO.setup(humidity, GPIO.IN)
    logging.info(f'configured pin {water_open} as output to open the water, pin {water_close} as output to close the water, GPIO mode is {GPIO.getmode()}')
    logging.info(f'turning off the water (if it was closed already no change)')
    switch(water_close)
    water_status = 0
    # set up the range of time to open the water
    start = datetime.strptime(args.start,"%H:%M").time()
    end = datetime.strptime(args.end,"%H:%M").time()
    while True:
        h1 = GPIO.input(humidity)
        if check_time(start, end, datetime.now().time()):
            if water_status == 0:
                logging.info(f'time is {datetime.now().time().strftime("%H:%M")}, turning on the water')
                switch(water_open)
            # read the humidity of the ground and report it --> if it increases and the sensor is set in a reasonable place, it means the watering is working
            if (GPIO.input(humidity) - h1) > th:
                h2 = GPIO.input(humidity)
                report = f'humidity of soil is increasing by {h2-h1}% since 1 minute ago, watering system is effective!'
            elif GPIO.input(humidity) < h1 and (GPIO.input(humidity) - h1) > th:
                report = f'soil is drying up'
            else:
                report = f'soil humidity has not changed yet'
            logging.info(f'time is {datetime.now().time().strftime("%H:%M")}, keeping water on, pin state is {GPIO.input(water_open)}, {report}')
            water_status = 1
        else:
            if water_status == 1:
                logging.info(f'time is {datetime.now().time().strftime("%H:%M")}, turning off the water')
                switch(water_close)
            logging.info(f'time is {datetime.now().time().strftime("%H:%M")}, water is off, humidity is {h1}')
            water_status = 0
        # sleep 1 minute to avoid too fast changes
        time.sleep(time_switch)
    

