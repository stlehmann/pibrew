import unittest
from pibrew import create_app, socketio, brew_controller


class PiBrewTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.process_interval = self.app.config['PROCESS_INTERVAL']
        self.client.get('/')

    def tearDown(self):
        pass

    def test_default_config(self):
        self.app = create_app()
        self.assertFalse(self.app.config['TESTING'])
        self.assertFalse(self.app.config['SIMULATE'])

    def test_index(self):
        rv = self.client.get('/')
        self.assertEqual(200, rv.status_code)

    def test_settings(self):
        # test get
        rv = self.client.get('settings/')
        self.assertEqual(200, rv.status_code)

        # test cancel post
        form = {'kp': 100.0, 'tn': 20.0, 'cancel': 'cancel'}
        rv = self.client.post('settings/', data=form)

        # test submit post
        form = {'kp': 100.0, 'tn': 20.0, 'submit': 'submit'}
        rv = self.client.post('settings/', data=form)

    def test_connect(self):
        client = socketio.test_client(self.app)
        received = client.get_received()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0]['args'], 'connected')

    def test_enable_heater(self):
        client = socketio.test_client(self.app)
        client.get_received()

        # enable heater
        client.emit('enable heater')
        received = client.get_received()
        self.assertEqual('heater enabled', received[0]['name'])
        self.assertTrue(brew_controller.heater_enabled)

        # wait for one process cycle
        socketio.sleep(self.process_interval)
        received = client.get_received()
        self.assertEqual('update', received[0]['name'])

        # disable heater
        client.emit('disable heater')
        received = client.get_received()
        self.assertEqual('heater disabled', received[0]['name'])
        self.assertFalse(brew_controller.heater_enabled)

        # wait for one process cycle
        socketio.sleep(self.process_interval)
        received = client.get_received()
        self.assertEqual('update', received[0]['name'])

    def test_enable_mixer(self):
        client = socketio.test_client(self.app)
        client.get_received()

        # enable mixer
        client.emit('enable mixer')
        received = client.get_received()
        self.assertEqual('mixer enabled', received[0]['name'])
        self.assertTrue(brew_controller.mixer_enabled)

        # wait for one process cycle
        socketio.sleep(self.process_interval)
        received = client.get_received()
        self.assertEqual('update', received[0]['name'])

        # disable mixer
        client.emit('disable mixer')
        received = client.get_received()
        self.assertEqual('mixer disabled', received[0]['name'])
        self.assertFalse(brew_controller.mixer_enabled)

        # wait for one process cycle
        socketio.sleep(self.process_interval)
        received = client.get_received()
        self.assertEqual('update', received[0]['name'])

    def test_change_setpoint(self):
        client = socketio.test_client(self.app)
        client.get_received()

        # change setpoint
        client.emit('change setpoint', {'value': 99})
        received = client.get_received()
        self.assertEqual('setpoint changed', received[0]['name'])
        self.assertEqual('99.0', received[0]['args'][0]['value'])

    def test_load_data(self):
        client = socketio.test_client(self.app)
        client.get_received()

        # change setpoint
        client.emit('load data')
        received = client.get_received()
        data = received[0]['args'][0]
        self.assertIsInstance(data, dict)

        for key in ['t', 'temp_ct', 'temp_sp', 'ht_pwr']:
            self.assertIn(key, data)
