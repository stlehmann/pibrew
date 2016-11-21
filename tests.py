import sys
import coverage
import subprocess
import unittest


cov = coverage.Coverage(branch=True)
cov.start()

from pibrew import app, socketio
app.config['TESTING'] = True


class PiBrewTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_connect(self):
        client = socketio.test_client(app)
        client.get_received()


if __name__ == '__main__':
    tests_ok = unittest.main(verbosity=2, exit=False).result.wasSuccessful()

    # print coverage report
    cov.stop()
    print('')
    cov.report(omit=['tests.py', 'venv/*'])

    # lint the code
    print('')
    lint_ok = subprocess.call(['flake8', '--ignore=E402', 'pibrew.py',
                               'tests.py']) == 0

    sys.exit((0 if tests_ok else 1) + (0 if lint_ok else 2))
