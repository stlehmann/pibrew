import logging
import sys
from datetime import datetime
from . import db
from .models import Setting
from .hardware import HdwRaspberry, HdwSimulator
from .controllers import TempController, PWM_DC
from .sequence import Sequence


logger = logging.getLogger(__file__)


class Settings:
    defaults = {
        'temp_setpoint': 50.0,
        'kp': 10.0,
        'tn': 180.0,
        'manual_power_pct': 0.0,
        'duty_cycle_s': 60.0
    }
    app = None

    def __init__(self, app):
        self.app = app

    def __getattr__(self, name):
        with self.app.app_context():
            setting = Setting.query.filter_by(name=name).first()
            if setting is None:
                default = Settings.defaults.get(name)
                if default is not None:
                    setting = Setting(name=name, value=default)
                    db.session.add(setting)
                    db.session.commit()
                else:
                    return AttributeError(
                        'There is no setting called {}'.format(name)
                    )
            else:
                return setting.value

    def __setattr__(self, name, value):
        if name in ('app', ):
            super().__setattr__(name, value)
        else:
            with self.app.app_context():
                setting = Setting.query.filter_by(name=name).first()
                if setting is None:
                    setting = Setting(name=name, value=value)
                    db.session.add(setting)
                    db.session.commit()
                else:
                    setting.value = value
                    db.session.commit()


class BrewController():
    """
    BrewController is controlling the I/Os of the Raspberry Pi or
    if no I/Os can be found it will simulate the signals. The singleton pattern
    is chosen because on a system there should always only be one
    BrewController to address hardware independent of the number of Flask
    clients. Use `get_instance` function to get only one instance. For
    testing purposes use constructor directly.

    """
    @classmethod
    def get_instance(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(self, app=None):
        self.initialized = False
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        if self.initialized:
            raise RuntimeError('BrewController can only be initialized once.')

        self.initialized = True
        self.simulate = app.config['SIMULATE']

        self.temp_controller = TempController()
        self.temp_pwm = PWM_DC()
        self.sequence = Sequence(app, self)

        self.heater_enabled = False
        self.mixer_enabled = False
        self.temp_current = 0.0
        self.temp_ctrl_reset = False
        self.manual = False
        self.reset = False

        self.settings = Settings(app)

        if self.simulate:
            self.hdw_interface = HdwSimulator()
        else:
            # running on linux?
            if sys.platform == 'linux':  # pragma: no cover
                try:
                    self.hdw_interface = HdwRaspberry()
                except IOError:
                    logger.error('No temperature sensor found.'
                                 'Continuing in simulation mode.')
                    self.hdw_interface = HdwSimulator()
            else:
                logger.warning('Platform is not Linux. Continuing in '
                               'simulation mode.')
                self.hdw_interface = HdwSimulator()

    def process(self):
        # get current time to pass to the controllers
        self.now = datetime.now()

        # read the current temperature
        self.temp_current = self.hdw_interface.read_temp()

        # process sequence controller
        self.sequence.process(self.temp_current, self.now)

        # process temperature controller
        heater_power_pct = self.temp_controller.process(
            enable=self.heater_enabled,
            now=self.now,
            temp_current=self.temp_current,
            temp_setpoint=self.settings.temp_setpoint,
            kp=self.settings.kp,
            tn=self.settings.tn,
            manual=self.manual,
            manual_power_pct=self.settings.manual_power_pct,
            reset=self.reset
        )

        # process duty cycle controller
        heater_output = self.temp_pwm.process(
            now=self.now,
            enable=self.heater_enabled,
            in_pct=heater_power_pct,
            duty_cycle_s=self.settings.duty_cycle_s,
        )

        # set output of the heater according to the temperature controller
        self.hdw_interface.set_heater_output(heater_output)
        self.hdw_interface.set_mixer_output(self.mixer_enabled)

    # temp_setpoint property
    @property
    def temp_setpoint(self):
        return self.settings.temp_setpoint

    @temp_setpoint.setter
    def temp_setpoint(self, value):
        self.settings.temp_setpoint = value

    # manual_power_pct property
    @property
    def manual_power_pct(self):
        return self.settings.manual_power_pct

    @manual_power_pct.setter
    def manual_power_pct(self, value: float):
        self.settings.manual_power_pct = value

    # kp property
    @property
    def kp(self):
        return self.settings.kp

    @kp.setter
    def kp(self, value: float):
        self.settings.kp = value

    # tn property
    @property
    def tn(self):
        return self.settings.tn

    @tn.setter
    def tn(self, value: float):
        self.settings.tn = value

    # duty cycle property
    @property
    def duty_cycle_s(self):
        return self.settings.duty_cycle_s

    @duty_cycle_s.setter
    def duty_cycle_s(self, value):
        self.settings.duty_cycle_s = value

    # heater power property
    @property
    def heater_power_pct(self):
        return self.temp_controller.power

    # heater on property
    @property
    def heater_on(self):
        """ True if the heater is currently powered """
        return self.temp_pwm.output
