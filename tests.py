import coverage
import sys
import subprocess
import unittest

CHECK_COVERAGE = True

if CHECK_COVERAGE:
    cov = coverage.Coverage(branch=True)
    cov.start()


from pibrew import app, socketio, brew_controller


class PiBrewTest(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        pass

    def test_index(self):
        rv = self.client.get('/')
        self.assertEqual(200, rv.status_code)

    def test_connect(self):
        client = socketio.test_client(app)
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'], 'connected')

    def test_enable_heater(self):
        client = socketio.test_client(app)
        client.get_received()
        # enable heater
        client.emit('enable heater')
        received = client.get_received()
        self.assertEqual('heater enabled', received[0]['name'])
        self.assertTrue(brew_controller.heater_enabled)
        # disable heater
        client.emit('disable heater')
        received = client.get_received()
        self.assertEqual('heater disabled', received[0]['name'])
        self.assertFalse(brew_controller.heater_enabled)

    def test_enable_mixer(self):
        client = socketio.test_client(app)
        client.get_received()
        # enable heater
        client.emit('enable mixer')
        received = client.get_received()
        self.assertEqual('mixer enabled', received[0]['name'])
        self.assertTrue(brew_controller.mixer_enabled)
        # disable heater
        client.emit('disable mixer')
        received = client.get_received()
        self.assertEqual('mixer disabled', received[0]['name'])
        self.assertFalse(brew_controller.mixer_enabled)


if __name__ == '__main__':
    tests_ok = unittest.main(verbosity=2, exit=False).result.wasSuccessful()

    # print coverage report
    if CHECK_COVERAGE:
        cov.stop()
        print('')
        cov.report(omit=['tests.py', 'venv/*'], show_missing=True)
        cov.html_report(omit=['tests.py', 'venv/*'])

    # lint the code
    print('')
    lint_ok = subprocess.call(['flake8', '--ignore=E402', 'pibrew.py',
                               'tests.py']) == 0

    sys.exit((0 if tests_ok else 1) + (0 if lint_ok else 2))
