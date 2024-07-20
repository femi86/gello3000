import RPi.GPIO as GPIO
import time
import logging

logger = logging.getLogger(__name__)
class raspiStation():
    def __init__(self, config):
        GPIO.setmode(GPIO.BOARD)
        self.pins = {}
        for pin_name in config.keys():
            pin_number = config[pin_name]['pinN']
            mode = config[pin_name]['mode']
            GPIO.setup(pin_number, mode)
            logger.info(f'configured pin {pin_name} as {str(mode)}')
            self.pins[pin_name] = pin_number


    def switch(self,pinname, time_switch):
        GPIO.output(self.pins[pinname],1)
        logger.info(f'pin {pinname} is {GPIO.input(self.pins[pinname])} for {time_switch} seconds')
        time.sleep(time_switch)
        GPIO.output(self.pins[pinname],0)
        logger.info(f'turning pin {pinname} off, pin state is {GPIO.input(self.pins[pinname])}')

    def read(self,pinname):
        logger.info(f' reading value from pin {pinname}')
        return GPIO.input(self.pins[pinname])

    def total_flow(analog_value):
        # this function should calculate the volume of water flown in liters
        pass

