from wtforms import Field
from wtforms_components.widgets import TimeInput
from utils import s_to_hms, hms_to_s


class TimespanField(Field):
    widget = TimeInput(step=1)

    def __init__(self, label=None, validators=None, **kwargs):
        super().__init__(label, validators, **kwargs)

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            return (
                self.data and
                '{:02}:{:02}:{:02}'.format(*s_to_hms(self.data)) or ''
            )

    def process_formdata(self, valuelist):
        if valuelist:
            time_str = ' '.join(valuelist)
            try:
                self.data = hms_to_s(*map(int, time_str.split(':')))
            except (ValueError, TypeError):
                self.data = None
                raise ValueError(self.gettext('Not a valid time value'))
