import logging
from . import socketio, brew_controller, process_data

logger = logging.getLogger(__name__)


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


@socketio.on('change setpoint')
def on_change_setpoint(data):
    sp = float(data['value'])
    brew_controller.temp_setpoint = sp
    socketio.emit('setpoint changed', {'value': '{:.1f}'.format(sp)})


@socketio.on('load data')
def on_load_data():
    logger.debug('Socket: init data')
    socketio.emit('init data', process_data)


@socketio.on('start sequence')
def on_start_sequence():
    logger.debug('sequence started')
    socketio.emit('sequence started')


@socketio.on('stop sequence')
def on_stop_sequence():
    logger.debug('sequence stopped')
    socketio.emit('sequence stopped')