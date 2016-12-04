import os
import time
import threading
import logging
import arrow
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from flaskext.lesscss import lesscss

from config import config
from .brewcontroller import BrewController


logger = logging.getLogger(__name__)


background_thread = threading.Thread()

# Flask Plugins
bootstrap = Bootstrap()
socketio = SocketIO()
brew_controller = BrewController()
process_data = {'t': [], 'temp_sp': [], 'temp_ct': [], 'ht_pwr': []}

from . import events  # noqa


def create_app(config_name=None):
    app = Flask(__name__)

    # load config
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    app.config.from_object(config[config_name])

    # init logger
    app.logger.setLevel(app.config['LOG_LEVEL'])
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    app.logger.addHandler(stream_handler)

    app.logger.info('started application')

    # init flask plugins
    lesscss(app)
    bootstrap.init_app(app)
    socketio.init_app(app)

    # create blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')

    @app.before_first_request
    def init_brew_controller():
        # init the brew controller and start the background task if none
        # exists yet
        if not brew_controller.initialized:
            brew_controller.init_app(app)

            background_thread = threading.Thread(
                target=process_controller,
                args=[app.config['PROCESS_INTERVAL']],
                daemon=True
            )
            background_thread.start()
            app.logger.info('started background thread')

    return app


def process_controller(interval):
    while(1):
        current_time = arrow.now()
        brew_controller.process()

        data = {
            't': current_time.format('YYYY-MM-DD HH:mm:ss.SSS'),
            'temp_sp': '{:.1f}'.format(brew_controller.temp_setpoint),
            'temp_ct': '{:.1f}'.format(brew_controller.temp_current),
            'ht_en': brew_controller.heater_enabled,
            'mx_en': brew_controller.mixer_enabled,
            'ht_pwr': '{:.1f}'.format(brew_controller.heater_power_pct),
            'ht_on': brew_controller.heater_on,
        }

        # Only save every tenth value
        process_data['t'].append(data['t'])
        process_data['temp_sp'].append(data['temp_sp'])
        process_data['temp_ct'].append(data['temp_ct'])
        process_data['ht_pwr'].append(data['ht_pwr'])

        logger.debug(process_data['t'][-1])
        socketio.emit('update', data)
        time.sleep(interval)
