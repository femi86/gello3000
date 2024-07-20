#!/usr/bin/python3

from datetime import datetime
import time
import yaml
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

def total_flow(analog_value):
    # this function should calculate the volume of water flown in liters
    pass



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

def setup_rpi(config):
    """
    provide the config from the yaml where the pins are setup,
    it will parse the key,value pairs and set the pins appropriately

    """
    pin_names = {}
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BOARD)
    for pin_name in config.keys():
        pin_number = config[pin_name]['pinN']
        mode = config[pin_name]['mode']
        GPIO.setup(pin_number, mode)
        logging.info(f'configured pin {pin_name} as {str(mode)}')
        pin_names[pin_name] = pin_number
    return pin_names

if __name__=="__main__":
    logger_setup(logger)
    with open('UserSettings.yaml', 'r') as file:
        config = yaml.safe_load(file)
    water_status = 1
    time_switch = config['time-switch']
    #logger = logging.getLogger(__name__)
    pins = setup_rpi(config['rpi-pins'])

    logging.info(f'water will be turned on in the timerange: {time_switch}')

    logging.info(f'turning off the water (if it was closed already no change)')
    switch(pins['water_close'])
    water_status = 0
    # set up the range of time to open the water
    start = datetime.strptime(time_switch['start'],"%H:%M").time()
    end = datetime.strptime(time_switch['end'],"%H:%M").time()
    while True:
        # read operation.json file if it exists and check days since it worked
        before = datetime.now()
        h1 = GPIO.input(pins['humidity'])
        if check_time(start, end, datetime.now().time()):
            if water_status == 0:
                # dump into summary.log start time
                # start measuring the flow into a total_water
                logging.info(f'time is {datetime.now().time().strftime("%H:%M")}, turning on the water')
                switch(pins['water_open'])
            # read the humidity of the ground and report it --> if it increases and the sensor is set in a reasonable place, it means the watering is working
            if (GPIO.input(pins['humidity']) - h1) > th:
                h2 = GPIO.input(pins['humidity'])
                report = f'humidity of soil is increasing by {h2-h1}% since 1 minute ago, watering system is effective!'
            elif GPIO.input(pins['humidity']) < h1 and (GPIO.input(pins['humidity']) - h1) > th:
                report = f'soil is drying up'
            else:
                report = f'soil humidity has not changed yet'
            logging.info(f'time is {datetime.now().time().strftime("%H:%M")}, keeping water on, pin state is {GPIO.input(pins['water-open'])}, {report}')
            water_status = 1
        else:
            if water_status == 1:
                # dump into summary.log end time and total flow
                logging.info(f'time is {datetime.now().time().strftime("%H:%M")}, turning off the water')
                switch(pins['water-close'])
            logging.info(f'time is {datetime.now().time().strftime("%H:%M")}, water is off, humidity is {h1}')
            water_status = 0
        time.sleep(time_switch) # sleep 1 minute to avoid too fast changes
        now = datetime.now()
        # insert here check if the date has changed,
        # 1. read the operations.json file
        # 2. check whether the date is different, if yes increase the counter, if not don't do anything
    

