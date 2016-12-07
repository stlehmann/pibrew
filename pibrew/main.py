from flask_wtf import Form
from wtforms import DecimalField, SubmitField
from wtforms.validators import Required, NumberRange
from flask import Blueprint, render_template, redirect, url_for
from . import brew_controller


main = Blueprint('main', __name__)


class SettingsForm(Form):
    # proportional part KP of controller
    kp = DecimalField('KP', places=2,
                      validators=[Required(), NumberRange(min=0.0, max=100.0)])

    # integral part TN of controller
    tn = DecimalField('TN', places=2,
                      validators=[Required(), NumberRange(min=0.0, max=1000.0)])

    submit = SubmitField()


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


@main.route('settings/', methods=['GET', 'POST'])
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        brew_controller.kp = float(form.kp.data)
        brew_controller.tn = float(form.tn.data)
        return redirect(url_for('main.index'))
    else:
        form.kp.data = brew_controller.kp
        form.tn.data = brew_controller.tn
    return render_template('settings.html', form=form)