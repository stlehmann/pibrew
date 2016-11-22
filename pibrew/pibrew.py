import os
import arrow
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from config import config


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


def handle_controller():
    interval = app.config['PROCESS_INTERVAL']
    while(1):
        current_time = arrow.now()
        brew_controller.process()
        socketio.emit(
            'update',
            {
                'time': current_time.for_json(),
                'temp_setpoint': brew_controller.temp_setpoint,
                'temp_current': brew_controller.temp_current
            }
        )
        socketio.sleep(interval)


app = Flask(__name__)
app.config.from_object(config[os.environ.get('PIBREW_CONFIG', 'development')])

# Flask Plugins
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
socketio = SocketIO(app)
brew_controller = BrewController(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def on_connect():
    socketio.send('connected')


@socketio.on('enable heater')
def on_enable_heater():
    brew_controller.heater_enabled = True
    socketio.emit('heater enabled')


@socketio.on('disable heater')
def on_disable_heater():
    brew_controller.heater_enabled = False
    socketio.emit('heater disabled')


@socketio.on('enable mixer')
def on_enable_mixer():
    brew_controller.mixer_enabled = True
    socketio.emit('mixer enabled')


@socketio.on('disable mixer')
def on_disable_mixer():
    brew_controller.mixer_enabled = False
    socketio.emit('mixer disabled')


# start the background task
socketio.start_background_task(target=handle_controller)


if __name__ == '__main__':  # pragma: no cover
    socketio.run(app)
