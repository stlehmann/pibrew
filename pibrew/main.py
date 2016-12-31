import logging
from flask import jsonify
from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField, StringField, BooleanField
from wtforms.validators import NumberRange, Length, InputRequired
from flask import Blueprint, render_template, redirect, url_for, request
from . import brew_controller, db
from .fields import TimespanField
from .models import SequenceStep


main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)


class MyInputRequired(InputRequired):
    field_flags = ()


class SettingsForm(FlaskForm):
    # proportional part KP of controller
    kp = DecimalField('KP', places=2,
                      validators=[MyInputRequired(),
                                  NumberRange(min=0.0, max=100.0)])

    # integral part TN of controller
    tn = DecimalField('TN', places=2,
                      validators=[MyInputRequired(),
                                  NumberRange(min=0.0, max=1000.0)])

    submit = SubmitField('Speichern')
    cancel = SubmitField('Abbrechen')


class StepForm(FlaskForm):
    name = StringField('Name:', validators=[MyInputRequired(), Length(1, 128)])
    duration = TimespanField(
        'Dauer (hh:mm:ss):', validators=[MyInputRequired()])
    temperature = DecimalField(
        'Temperatur (°C):', places=1,
        validators=[MyInputRequired(), NumberRange(1, 100)])
    tolerance = DecimalField(
        'Toleranz (°C):', places=1, validators=[NumberRange(0, 20)])
    heater = BooleanField('Heizung')
    mixer = BooleanField('Mixer')

    submit = SubmitField('Speichern')
    cancel = SubmitField('Abbrechen')


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


@main.route('sequence/', methods=['GET', 'POST'])
def sequence():
    steps = SequenceStep.query.order_by(SequenceStep.order).all()
    return render_template('sequence.html', steps=steps)


@main.route('sequence/steps/add', methods=['GET', 'POST'])
def add_step():
    form = StepForm()
    if request.method == 'POST':
        if 'submit' in request.form:
            if form.validate_on_submit():
                step = SequenceStep()
                step.name = form.name.data
                step.duration = form.duration.data
                step.temperature = form.temperature.data
                step.tolerance = form.tolerance.data
                step.heater = form.heater.data
                step.mixer = form.mixer.data
                db.session.add(step)
                db.session.commit()
        return redirect(url_for('main.sequence'))
    return render_template('step.html', form=form)


@main.route('sequence/steps/<step_id>/edit', methods=['GET', 'POST'])
def edit_step(step_id):
    form = StepForm()
    step = SequenceStep.query.filter_by(id=step_id).first_or_404()
    if request.method == 'POST':
        if 'submit' in request.form:
            if form.validate_on_submit():
                step.name = form.name.data
                step.duration = form.duration.data
                step.temperature = form.temperature.data
                step.tolerance = form.tolerance.data
                step.heater = form.heater.data
                step.mixer = form.mixer.data
                db.session.add(step)
                db.session.commit()
        return redirect(url_for('main.sequence'))
    else:
        form.name.data = step.name
        form.duration.data = step.duration
        form.temperature.data = step.temperature
        form.tolerance.data = step.tolerance
        form.heater.data = step.heater
        form.mixer.data = step.mixer
    return render_template('step.html', form=form)


@main.route('sequence/steps/<step_id>/delete', methods=['DELETE'])
def delete_step(step_id):
    step = SequenceStep.query.filter_by(id=step_id).first()
    if step is None:
        return jsonify(
            status='error',
            message='no sequence step with id {}'.format(step_id)
        )
    db.session.delete(step)
    db.session.commit()
    return jsonify(status='ok')


@main.route('sequence/steps/<step_id>/up', methods=['POST'])
def move_step_up(step_id):
    step = SequenceStep.query.filter_by(id=step_id).first()
    if step is None:
        return jsonify(
            status='error',
            message='no sequence step with id {}'.format(step_id)
        )
    step.move_up()
    db.session.add(step)
    db.session.commit()
    return jsonify(status='ok')


@main.route('sequence/steps/<step_id>/down', methods=['POST'])
def move_step_down(step_id):
    step = SequenceStep.query.filter_by(id=step_id).first()
    if step is None:
        return jsonify(
            status='error',
            message='no sequence step with id {}'.format(step_id)
        )
    step.move_down()
    db.session.add(step)
    db.session.commit()
    return jsonify(status='ok')


@main.route('settings/', methods=['GET', 'POST'])
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        if 'submit' in request.form:
            brew_controller.kp = float(form.kp.data)
            brew_controller.tn = float(form.tn.data)
        return redirect(url_for('main.index'))
    else:
        form.kp.data = brew_controller.kp
        form.tn.data = brew_controller.tn
    return render_template('settings.html', form=form)
