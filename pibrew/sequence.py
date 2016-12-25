from datetime import datetime, timedelta
from . import db
from .models import SequenceStep

ACTION_START = 1
ACTION_STOP = 2
ACTION_PAUSE = 3
ACTION_BWD = 4
ACTION_FWD = 5

STATE_STOPPED = 0
STATE_RUNNING = 1
STATE_PAUSED = 2
STATE_FINISHED = 3

STEP_STATE_NOTHING = 0
STEP_STATE_HEATING = 1
STEP_STATE_HOLDING = 2
STEP_STATE_FINISHED = 3


class Sequence:

    def __init__(self, app, brew_ctl):
        self.app = app
        self.brew_ctl = brew_ctl
        self.steps = []
        self.start_time = None
        self.cur_step_id = None
        self.time_total = timedelta()
        self.time_cur_step = timedelta()
        self.time_prev = None
        self.cur_step_state = STEP_STATE_NOTHING
        self.pending_actions = []
        self.state = STATE_STOPPED

    def update_steps(self):
        with self.app.app_context():
            self.steps = SequenceStep.query.order_by(SequenceStep.order).all()
            [db.session.expunge(x) for x in self.steps]

    def start(self):
        self.pending_actions.append(ACTION_START)

    def stop(self):
        self.pending_actions.append(ACTION_STOP)

    def pause(self):
        self.pending_actions.append(ACTION_PAUSE)

    def bwd(self):
        self.pending_actions.append(ACTION_BWD)

    def fwd(self):
        self.pending_actions.append(ACTION_FWD)

    def process(self, temperature: float, cur_time: datetime):

        # process all pending actions
        while len(self.pending_actions):
            action = self.pending_actions.pop()

            if action == ACTION_START:
                if self.state == STATE_STOPPED:
                    self.update_steps()
                    if len(self.steps):
                        self.cur_step_id = 0
                        self.start_time = cur_time
                        self.state = STATE_RUNNING

            elif action == ACTION_STOP:
                self.state = STATE_STOPPED

            elif action == ACTION_PAUSE:
                if self.state == STATE_RUNNING:
                    self.state = STATE_PAUSED

            elif (action == ACTION_FWD and len(self.steps) and
                    self.cur_step_id < len(self.steps) - 1):
                self.cur_step_id += 1

            elif (action == ACTION_BWD and len(self.steps) and
                    self.cur_step_id > 0):
                self.cur_step_id -= 1

        # time counter for the whole sequence
        if self.state not in (STATE_FINISHED, STATE_STOPPED):
            self.time_total = cur_time - self.start_time

        # state handling
        if self.state == STATE_RUNNING:
            cur_step = self.steps[self.cur_step_id]

            if self.cur_step_state == STEP_STATE_NOTHING:
                self.brew_ctl.temp_setpoint = cur_step.temperature
                self.brew_ctl.heater_enabled = cur_step.heater
                self.brew_ctl.mixer_enabled = cur_step.mixer
                self.cur_step_state = STEP_STATE_HEATING

            # HEATING until setpoint is reached
            if self.cur_step_state == STEP_STATE_HEATING:
                if temperature >= (cur_step.temperature - cur_step.tolerance):
                    self.cur_step_state = STEP_STATE_HOLDING

            # HOLD temperature for time
            elif self.cur_step_state == STEP_STATE_HOLDING:
                if self.time_cur_step < self.steps[self.cur_step_id].duration:
                    self.time_cur_step += cur_time - self.time_prev
                else:
                    self.cur_step_state = STEP_STATE_FINISHED

            elif self.cur_step_state == STEP_STATE_FINISHED:
                if self.cur_step_id < len(self.steps) - 1:
                    self.cur_step_state = STEP_STATE_HEATING
                    self.cur_step_id += 1
                else:
                    self.state = STATE_FINISHED

        self.time_prev = cur_time

    def get_data(self):
        return {
            'state': self.state,
            'cur_step_state': self.cur_step_state,
            'cur_step_id': self.cur_step_id,
            'time_total': '{}'.format(self.time_total),
            'time_cur_step': '{}'.format(self.time_cur_step)
        }
