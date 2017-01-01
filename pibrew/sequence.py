from datetime import datetime, timedelta
from .models import SequenceStep
from . import socketio
from utils import s_to_hms

ACTION_START = 1
ACTION_STOP = 2
ACTION_PAUSE = 3
ACTION_BWD = 4
ACTION_FWD = 5

STATE_STOPPED = 0
STATE_RUNNING = 1
STATE_PAUSED = 2
STATE_FINISHED = 3


class Step:

    STATE_WAITING = 0
    STATE_HEATING = 1
    STATE_HOLDING = 2
    STATE_FINISHED = 3
    STATE_SKIPPED = 4

    def __init__(self, sequence, sequence_step: SequenceStep):
        self.sequence = sequence
        self.brew_ctl = sequence.brew_ctl
        self.state = self.STATE_WAITING
        self.passed_seconds = 0
        self.id = sequence_step.id
        self.duration = sequence_step.duration
        self.tolerance = sequence_step.tolerance
        self.temperature = sequence_step.temperature
        self.heater = sequence_step.heater
        self.mixer = sequence_step.mixer

    def process(self, dt_s: float, temperature):
        if self.state == self.STATE_WAITING:
            self.brew_ctl.temp_setpoint = self.temperature
            self.brew_ctl.heater_enabled = self.heater
            self.brew_ctl.mixer_enabled = self.mixer
            self.state = self.STATE_HEATING

        # HEATING until setpoint is reached
        elif self.state == self.STATE_HEATING:
            if temperature >= (self.temperature - self.tolerance):
                self.state = self.STATE_HOLDING

        # HOLD temperature for time
        elif self.state == self.STATE_HOLDING:
            if self.passed_seconds < self.duration:
                self.passed_seconds += dt_s
            else:
                self.state = self.STATE_FINISHED

        return self.state


class Sequence:

    def __init__(self, app, brew_ctl):
        self.app = app
        self.brew_ctl = brew_ctl
        self.steps = []
        self.cur_step_index = -1
        self.start_time = None
        self.time_total = timedelta()
        self.prev_time = None
        self.pending_actions = []
        self.state = STATE_STOPPED

    def create_steps(self):
        with self.app.app_context():
            steps = SequenceStep.query.order_by(SequenceStep.order).all()
            return [Step(self, x) for x in steps]

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

    @property
    def cur_step(self):
        return self.steps[self.cur_step_index]

    def process(self, temperature: float, cur_time: datetime):
        if self.prev_time is None:
            self.prev_time = cur_time

        dt_s = (cur_time - self.prev_time).total_seconds()

        # process all pending actions
        while len(self.pending_actions):
            action = self.pending_actions.pop()

            if action == ACTION_START:
                if self.state == STATE_STOPPED:
                    self.steps = self.create_steps()
                    if len(self.steps):
                        self.cur_step_index = 0
                        self.start_time = cur_time
                        self.state = STATE_RUNNING

            elif action == ACTION_STOP:
                self.state = STATE_FINISHED

            elif action == ACTION_PAUSE:
                if self.state == STATE_RUNNING:
                    self.state = STATE_PAUSED

            elif (action == ACTION_FWD and
                    self.cur_step_index < len(self.steps) - 1):
                self.cur_step_index += 1

            elif (action == ACTION_BWD and
                    self.cur_step_index > 0):
                self.cur_step_index -= 1

        # time counter for the whole sequence
        if self.state not in (STATE_FINISHED, STATE_STOPPED):
            self.time_total = cur_time - self.start_time

        # state handling
        if self.state == STATE_RUNNING:

            # process current step
            step_state = self.cur_step.process(dt_s, temperature)

            if step_state in (Step.STATE_FINISHED, Step.STATE_SKIPPED):
                if self.cur_step_index < len(self.steps) - 1:
                    self.cur_step_index += 1
                else:
                    self.state = STATE_FINISHED

        elif self.state == STATE_FINISHED:
            self.brew_ctl.heater_enabled = False
            self.brew_ctl.mixer_enabled = False
            socketio.emit('sequence stopped')
            self.state = STATE_STOPPED

        self.prev_time = cur_time

    def get_data(self):
        data = {
            'state': self.state,
            'time_total': '{:02}:{:02}:{:02}'.format(
                *map(int, s_to_hms(max(0, self.time_total.total_seconds())))
            ),
        }

        if self.state in (STATE_RUNNING, STATE_FINISHED):
            data.update({
                'cur_step_state': self.cur_step.state,
                'cur_step_id': self.cur_step.id,
                'step_states': {x.id: x.state for x in self.steps},
                'time_cur_step': '{:02}:{:02}:{:02}'.format(
                    *map(int, s_to_hms(
                        max(0, self.cur_step.duration -
                            self.cur_step.passed_seconds)
                    ))
                )
            })

        return data