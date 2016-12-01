import os
import time
import threading
import arrow
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from flaskext.lesscss import lesscss

from config import config
from .brewcontroller import BrewController

background_thread = threading.Thread()

# Flask Plugins
bootstrap = Bootstrap()
socketio = SocketIO()
brew_controller = BrewController()

from . import events  # noqa


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name is None:
        config_name = os.environ.get('PIBREW_CONFIG', 'development')
    app.config.from_object(config[config_name])

    # init flask plugins
    lesscss(app)
    bootstrap.init_app(app)
    socketio.init_app(app)

    # create blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')

    # init the brew controller and start the background task if none
    # exists yet
    if not brew_controller.initialized:
        brew_controller.init_app(app)

        background_thread = threading.Thread(
            target=process_controller, args=[app.config['PROCESS_INTERVAL']],
            daemon=True
        )
        background_thread.start()

    return app


def process_controller(interval):

    while(1):

        current_time = arrow.now()
        brew_controller.process()
        socketio.emit(
            'update',
            {
                't': current_time.format('HH:mm:ss'),
                'temp_sp': '{:.1f}'.format(brew_controller.temp_setpoint),
                'temp_ct': '{:.1f}'.format(brew_controller.temp_current),
                'ht_en': brew_controller.heater_enabled,
                'mx_en': brew_controller.mixer_enabled,
                'ht_pwr': '{:.1f}'.format(brew_controller.heater_power_pct)
            }
        )
        time.sleep(interval)
