from . import db


class OrderableMixin:

    order = db.Column(db.Integer, index=True)

    def _get_model_class(self):
        for c in db.Model._decl_class_registry.values():
            if (    hasattr(c, '__tablename__')
                    and c.__tablename__ == self.__tablename__):
                return c

    def __init__(self):
        self._model = self._get_model_class()

        if self._model.query.count() == 0:
            self.order = 0
        else:
            self.order = max((item.order for item in self._model.query)) + 1

    def move_up(self):
        self._model = self._get_model_class()
        items = self._model.query.order_by(self._model.order).all()
        id_ = items.index(self)

        # if first item then do nothing
        if id_ == 0:
            return

        # get the item before which we swap position with
        item_before = items[id_ - 1]

        # swap order numbers with the item before
        x = self.order
        self.order = item_before.order
        item_before.order = x

        db.session.add(self)
        db.session.add(item_before)
        db.session.commit()

        # normalize order numbers for all items
        for i, item in enumerate(self._model.query.order_by(self._model.order)):
            item.order = i
        db.session.commit()

    def move_down(self):
        self._model = self._get_model_class()
        items = self._model.query.order_by(self._model.order).all()
        id_ = items.index(self)

        # if first item then do nothing
        if id_ == len(items) - 1:
            return

        # get the item before which we swap position with
        item_after = items[id_ + 1]

        # swap order numbers with the item before
        x = self.order
        self.order = item_after.order
        item_after.order = x

        db.session.add(self)
        db.session.add(item_after)
        db.session.commit()

        # normalize order numbers for all items
        for i, item in enumerate(self._model.query.order_by(self._model.order)):
            item.order = i
        db.session.commit()


class Setting(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    value = db.Column(db.Float)


class SequenceStep(db.Model, OrderableMixin):
    __tablename = 'sequence_steps'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    duration = db.Column(db.Time)
    temperature = db.Column(db.Float(precision=1))
    tolerance = db.Column(db.Float(precision=1))
    heater = db.Column(db.Boolean)
    mixer = db.Column(db.Boolean)

    def __init__(self):
        db.Model.__init__(self)
        OrderableMixin.__init__(self)
