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

    return app


if __name__ == '__main__':  # pragma: no cover
    socketio.run(create_app())
