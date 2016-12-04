from flask import Blueprint, render_template
from . import brew_controller


main = Blueprint('main', __name__)


@main.route('/')
def index():

    return render_template(
        'index.html',
        temp_setpoint=brew_controller.temp_setpoint,
        temp_current=brew_controller.temp_current,
        heater_enabled=brew_controller.heater_enabled,
        mixer_enabled=brew_controller.mixer_enabled,
        heater_power_pct=brew_controller.heater_power_pct,
    )
