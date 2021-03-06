import unittest
import arrow
from pibrew import create_app, db, brew_controller
from pibrew.models import SequenceStep
import pibrew.sequence as seq


class DummyStep:
    def __init__(self, *args, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


class SequenceTestCase(unittest.TestCase):

    def setUp(self):
        brew_controller.initialized = False
        self.app = create_app('testing')

        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self.client = self.app.test_client()
        self.process_interval = self.app.config['PROCESS_INTERVAL']
        self.client.get('/')

        self.sequence = brew_controller.sequence

        steps = [
            SequenceStep(
                name='Einmaischen',
                duration=300,
                temperature=54.0,
                tolerance=2.0
            ),
            SequenceStep(
                name='Maltoserast',
                duration=45 * 60,
                temperature=63.0,
                tolerance=2.0
            ),
            SequenceStep(
                name='Verzuckerungsrast',
                duration=30 * 60,
                temperature=72.0,
                tolerance=2.0
            )
        ]
        db.session.add_all(steps)
        db.session.commit()

    def tearDown(self):
        brew_controller.stop()
        while brew_controller.running:
            pass

        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_actions(self):
        s = self.sequence
        self.assertEqual(seq.STATE_STOPPED, s.state)
        s.start()
        s.process(50.0, arrow.now())
        self.assertEqual(seq.STATE_RUNNING, s.state)
        s.pause()
        s.process(50.0, arrow.now())
        self.assertEqual(seq.STATE_PAUSED, s.state)
        s.stop()
        s.process(50.0, arrow.now())
        self.assertEqual(seq.STATE_STOPPED, s.state)

        self.assertEqual(0, s.cur_step_index)
        s.fwd()
        s.process(50.0, arrow.now())
        self.assertEqual(1, s.cur_step_index)
        s.bwd()
        s.process(50.0, arrow.now())
        self.assertEqual(0, s.cur_step_index)


if __name__ == '__main__':
    unittest.main()
