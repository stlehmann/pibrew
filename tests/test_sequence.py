import unittest
from datetime import datetime
import pibrew.sequence as seq


class DummyStep:
    def __init__(self, *args, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)


class SequenceTestCase(unittest.TestCase):

    def setUp(self):
        self.sequence = seq.Sequence()
        steps = [
            DummyStep(
                name='Einmaischen',
                duration=datetime.strptime('00:05:00', '%H:%M:%S'),
                temperature=54.0,
                tolerance=2.0
            ),
            DummyStep(
                name='Maltoserast',
                duration=datetime.strptime('00:45:00', '%H:%M:%S'),
                temperature=63.0,
                tolerance=2.0
            ),
            DummyStep(
                name='Verzuckerungsrast',
                duration=datetime.strptime('00:30:00', '%H:%M:%S'),
                temperature=72.0,
                tolerance=2.0
            )
        ]
        self.sequence.update_steps(steps)

    def tearDown(self):
        pass

    def test_actions(self):
        s = self.sequence
        self.assertEqual(seq.STATE_STOPPED, s.state)
        s.start()
        s.process(datetime.now(), 50.0)
        self.assertEqual(seq.STATE_RUNNING, s.state)
        s.pause()
        s.process(datetime.now(), 50.0)
        self.assertEqual(seq.STATE_PAUSED, s.state)
        s.stop()
        s.process(datetime.now(), 50.0)
        self.assertEqual(seq.STATE_STOPPED, s.state)

        self.assertEqual(0, s.current_step_id)
        s.fwd()
        s.process(datetime.now(), 50.0)
        self.assertEqual(1, s.current_step_id)
        s.bwd()
        s.process(datetime.now(), 50.0)
        self.assertEqual(0, s.current_step_id)


if __name__ == '__main__':
    unittest.main()
