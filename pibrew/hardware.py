import os
import glob
import time
import timeit
import threading

class HdwInterface:  # pragma: no cover
    """ Only a common hardware interface """

    def __init__(self):
        pass

    def read_temp(self):
        raise NotImplementedError()

    def set_heater_output(self, val: bool):
        raise NotImplementedError()

    def set_mixer_output(self, val: bool):
        raise NotImplementedError()


class HdwRaspberry(HdwInterface):  # pragma: no cover
    """
    Hardware controller class for Raspberry Pi. Skip unittest on purpose
    because hardware can not be tested on development environment.

    """

    # Hardware configuration
    TEMPSENSOR = '28*'
    HEATER_PIN = 24
    MIXER_PIN = 23

    def __init__(self):

        super().__init__()

        # enable gpio and onewire functions
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        os.system('gpio export {pin} out'.format(pin=HdwRaspberry.HEATER_PIN))
        os.system('gpio export {pin} out'.format(pin=HdwRaspberry.MIXER_PIN))

        self.base_dir = '/sys/bus/w1/devices/'
        self.tempsensor_file = None
        self.cur_temp = 0
        self.thread = None

        # get the device file for the temperature sensor
        try:
            folder = glob.glob(self.base_dir + HdwRaspberry.TEMPSENSOR)[0]
        except IndexError:
            raise IOError('No temperature sensor found.')
        self.tempsensor_file = folder + '/w1_slave'

    def _read_raw_temp(self):
        while True:
            # read raw value from device file
            with open(self.tempsensor_file, 'r') as f:
                lines = f.readlines()

            # keep on reading until codeword 'YES' is found
            if lines[0].strip()[-3:] != 'YES':
                return

            # extract temperature
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos + 2:]
                temp_c = float(temp_string) / 1000.0
                self.cur_temp = temp_c

            # sleep for 10 seconds
            time.sleep(10.0)

    def read_temp(self):

        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._read_raw_temp)
            self.thread.start()

        return self.cur_temp


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
        super().__init__()
        self.temperature = 20.0
        self.heater_output = False
        self.mixer_output = False

    def read_temp(self):
        if self.heater_output:
            self.temperature += 1.0
        else:
            if self.temperature > 20.0:
                self.temperature -= 0.1
        return self.temperature

    def set_heater_output(self, val: bool):
        self.heater_output = val

    def set_mixer_output(self, val: bool):
        self.mixer_output = val
