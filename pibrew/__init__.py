import os
import time
import threading
import logging
import arrow
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flaskext.lesscss import lesscss

from config import config


logger = logging.getLogger('pibrew')
process_data = {'t': [], 'temp_sp': [], 'temp_ct': [], 'ht_pwr': []}
background_thread = threading.Thread()

# Flask Plugins
bootstrap = Bootstrap()
socketio = SocketIO()
db = SQLAlchemy()

from .brewcontroller import BrewController
brew_controller = BrewController()

from . import events  # noqa


def create_app(config_name=None):
    app = Flask(__name__)

    # load config
    if config_name is None:  # pragma: no cover
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    app.config.from_object(config[config_name])

    # init logger
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(app.config['LOG_LEVEL'])
    logger.setLevel(app.config['LOG_LEVEL'])
    logger.addHandler(stream_handler)

    app.logger.info('started application')

    # init flask plugins
    db.init_app(app)
    lesscss(app)
    bootstrap.init_app(app)
    socketio.init_app(app)

    # create blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint, url_prefix='/')

    @app.before_first_request
    def init_brew_controller():
        brew_controller.init_app(app)

    return app
