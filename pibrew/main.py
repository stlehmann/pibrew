import arrow
from flask import Blueprint, render_template
from . import socketio, brew_controller


main = Blueprint('main', __name__)


def process_controller():
    interval = brew_controller.app.config['PROCESS_INTERVAL']
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


@main.route('/')
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
socketio.start_background_task(target=process_controller)