from . import db


class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    value = db.Column(db.Float)


class SequenceStep(db.Model):
    __tablename = 'sequence_steps'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    duration = db.Column(db.Time)
    temperature = db.Column(db.Float(precision=1))
    tolerance = db.Column(db.Float(precision=1))
    heater = db.Column(db.Boolean)
    mixer = db.Column(db.Boolean)
