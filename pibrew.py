import arrow
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO


class BrewController():
    def __init__(self, app=None):
        if app is None:
            return
        self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.heater_enabled = False
        self.mixer_enabled = False


def handle_controller():
    while(1):
        current_time = arrow.now()
        socketio.emit('update', {'time': current_time.for_json()})
        socketio.sleep(1)


app = Flask(__name__)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
brew_controller = BrewController(app)

# add flask socketio and start a background task
socketio = SocketIO(app)
socketio.start_background_task(target=handle_controller)


@app.route('/')
def index():
    return render_template('index.html')


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


if __name__ == '__main__':
    socketio.run(app)
