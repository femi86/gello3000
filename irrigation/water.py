#!/usr/bin/python3

from datetime import datetime
import time
import yaml
import logging
from systemd.journal import JournalHandler
from raspiControl import raspiStation

logger = logging.getLogger("water.py")


def check_time(start,end,x):
    if start <= x <= end:
        return True
    else:
        return False

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
    with open('UserSettings.yaml', 'r') as file:
        config = yaml.safe_load(file)

    rpi = raspiStation(config['rpi-pins'])
    water_status = 1
    time_switch = config['time-switch']
    th = config['humidity-threshold']
    #logger = logging.getLogger(__name__)
    logging.info(f'water will be turned on in the timerange: {time_switch}')

    logging.info(f'turning off the water (if it was closed already no change)')
    rpi.switch('water_close',time_switch)
    water_status = 0
    # set up the range of time to open the water
    start = datetime.strptime(time_switch['start'],"%H:%M").time()
    end = datetime.strptime(time_switch['end'],"%H:%M").time()
    while True:
        # read operation.yaml file if it exists and check days since it worked
        before = datetime.now()

        h1 = rpi.read(rpi.pins['humidity'])
        if check_time(start, end, datetime.now().time()):
            if water_status == 0:
                # dump into summary.log start time
                # implement the flow meter start here
                logging.info(f'time is {datetime.now().time().strftime("%H:%M")}, turning on the water')
                rpi.switch('water_open', time_switch)
            # read the humidity of the ground and report it --> if it increases and the sensor is set in a reasonable place, it means the watering is working
            if (rpi.read('humidity') - h1) > th:
                h2 = rpi.read('humidity')
                report = f'humidity of soil is increasing by {h2-h1}% since 1 minute ago, watering system is effective!'
            elif rpi.read('humidity') < h1 and (rpi.read('humidity') - h1) > th:
                report = f'soil is drying up'
            else:
                report = f'soil humidity has not changed yet'
            # update the flow that has gone through
            logging.info(f'time is {datetime.now().time().strftime("%H:%M")}, keeping water on, pin state is {rpi.read('water-open')}, {report}')
            water_status = 1
        else:
            if water_status == 1:
                # dump into summary.log end time and total flow
                logging.info(f'time is {datetime.now().time().strftime("%H:%M")}, turning off the water')
                rpi.switch('water-close',time_switch)
            logging.info(f'time is {datetime.now().time().strftime("%H:%M")}, water is off, humidity is {h1}')
            water_status = 0
        time.sleep(time_switch) # sleep 1 minute to avoid too fast changes
        now = datetime.now()
        # insert here check if the date has changed,
        # 1. read the operations.json file
        # 2. check whether the date is different, if yes increase the counter, if not don't do anything
    

