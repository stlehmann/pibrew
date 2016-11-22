import arrow
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from .brewcontroller import BrewController
from config import config


# Flask Plugins
db = SQLAlchemy()
bootstrap = Bootstrap()
socketio = SocketIO()
brew_controller = BrewController()


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get('PIBREW_CONFIG', 'development')
    app.config.from_object(config[config_name])

    # init flask plugins
    db.init_app(app)
    bootstrap.init_app(app)
    socketio.init_app(app)
    brew_controller.init_app(app)

    # create blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')

    # start the background task
    socketio.start_background_task(target=process_controller)

    return app


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


if __name__ == '__main__':  # pragma: no cover
    socketio.run(create_app())
