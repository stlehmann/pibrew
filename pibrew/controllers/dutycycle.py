from datetime import datetime
from utils import default_if_none


class PWM_DC:

    def __init__(self):
        self._t0 = None
        self.enable = False
        self.in_pct = 0.0
        self.duty_cycle_s = 60.0
        self.output = False

    def process(self, now=datetime.now(), enable=None,
                in_pct=None, duty_cycle_s=None):

        # set values of optional parameters
        self.enable = default_if_none(enable, self.enable)
        self.in_pct = default_if_none(in_pct, self.in_pct)
        self.duty_cycle_s = default_if_none(duty_cycle_s, self.duty_cycle_s)

        # disable output if enable is false, if enable is set to true start
        # the duty cycle by setting _t0 to now.
        if not self.enable:
            self._t0 = None
            self.output = False
        else:
            if self._t0 is None:
                self._t0 = now

            # calculated delta to last process call
            t = now
            dt = (t - self._t0).total_seconds()

            # if delta bigger then duty set starttime t0 to current time
            if dt > self.duty_cycle_s:
                self._t0 = t
                dt = 0

            # calculate the on time during the cycle according to the input
            # value
            on_time = self.in_pct / 100.0 * self.duty_cycle_s
            self.output = False if self.in_pct == 0 else dt <= on_time

        return self.output
