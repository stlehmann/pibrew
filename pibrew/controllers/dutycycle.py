from datetime import datetime


class PWM_DC:

    def __init__(self):
        self._t0 = None
        self.enable = False
        self.in_pct = 0.0
        self.duty_cycle_s = 60.0
        self.out_pct = False

    def process(self, now=datetime.now(), enable=None,
                in_pct=None, duty_cycle_s=None):

        # set values of optional parameters
        if enable is not None:
            self.enable = enable

        if in_pct is not None:
            self.in_pct = in_pct

        if duty_cycle_s is not None:
            self.duty_cycle_s = duty_cycle_s

        # disable output if enable is false, if enable is set to true start
        # the duty cycle by setting _t0 to now.
        if not self.enable:
            self._t0 = None
            self.out_pct = False
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
            self.out_pct = False if in_pct == 0 else dt <= on_time

        return self.out_pct
