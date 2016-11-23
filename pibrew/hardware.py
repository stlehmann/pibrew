import os
import glob
import time
from config import base_dir


class HdwInterface:

    def __init__(self):
        pass


class HdwRaspberry(HdwInterface):

    # Hardware configuration
    TEMPSENSOR = '28*'
    HEATER_PIN = 24
    MIXER_PIN = 23

    def __init__(self):

        super().__init__(self)

        # enable gpio and onewire functions
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        os.system('gpio export {pin} out'.format(pin=HdwRaspberry.HEATER_PIN))
        os.system('gpio export {pin} out'.format(pin=HdwRaspberry.MIXER_PIN))

        self.base_dir = '/sys/bus/w1/devices/'
        self.tempsensor_file = None

        # get the device file for the temperature sensor
        try:
            folder = glob.glob(base_dir + HdwRaspberry.TEMPSENSOR)[0]
        except IndexError:
            raise IOError('No temperature sensor found.')
        self.tempsensor_file = folder + '/w1_slave'

    def _read_raw_temp(self):
        # read raw value from device file
        with open(self.tempsensor_file, 'r') as f:
            lines = f.readlines()
        return lines

    def read_temp(self):

        lines = self._read_raw_temp()

        # keep on reading until codeword 'YES' is found
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self._read_raw_temp()

        # extract temperature
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c

    def _set_output(self, pin: int, state: bool):
        os.system('gpio -g write {pin} {state}'.format(
            pin=pin, state=state)
        )

    def set_heater_output(self, val: bool):
        return self._set_output(
            pin=HdwRaspberry.HEATER_PIN, state=(1 if val else 0)
        )

    def set_mixer_output(self, val: bool):
        return self._set_output(
            pin=HdwRaspberry.MIXER_PIN, state=(1 if val else 0)
        )


class HdwSimulator(HdwInterface):

    def __init__(self):
        super().__init__(self)
