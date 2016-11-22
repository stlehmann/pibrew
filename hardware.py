import os


class HdwInterface:

    def __init__(self):
        pass


class HdwRaspberry(HdwInterface):

    # Hardware configuration
    TEMPSENSOR = '28*'
    HEATER_PIN = 24
    MIXER_PIN = 23

    def __init__(self):

        # enable gpio and onewire functions
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        os.system('gpio export {pin} out'.format(pin=HdwRaspberry.HEATER_PIN))
        os.system('gpio export {pin} out'.format(pin=HdwRaspberry.MIXER_PIN))

        self.base_dir = '/sys/bus/w1/devices/'
        super().__init__(self)


class HdwSimulator(HdwInterface):

    def __init__(self):
        super().__init__(self)