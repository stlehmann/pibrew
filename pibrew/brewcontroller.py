class BrewController():
    def __init__(self, app=None):
        if app is None:  # pragma: no cover
            return
        self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.heater_enabled = False
        self.mixer_enabled = False
        self.temp_setpoint = 50.0
        self.temp_current = 20.0

    def process(self):
        if self.temp_current < self.temp_setpoint:
            self.temp_current += 1
