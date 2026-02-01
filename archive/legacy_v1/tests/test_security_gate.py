import unittest
from unittest.mock import MagicMock, patch
import time
import sys
import os

# Add parent directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import config
from security_gate import AccessController

class TestAccessController(unittest.TestCase):

    @patch('security_gate.GunUI')
    def test_initial_state(self, MockGunUI):
        controller = AccessController()
        self.assertEqual(controller.state, "NIRODHA")
        self.assertEqual(controller.knock_count, 0)
        MockGunUI.assert_called()

    @patch('security_gate.GunUI')
    def test_process_knock_increment(self, MockGunUI):
        controller = AccessController()
        controller.process_knock()
        self.assertEqual(controller.knock_count, 1)

    @patch('security_gate.GunUI')
    def test_process_knock_timeout(self, MockGunUI):
        controller = AccessController()
        controller.process_knock()
        self.assertEqual(controller.knock_count, 1)

        # Simulate wait longer than timeout
        time.sleep(config.KNOCK_TIMEOUT + 0.1)

        controller.process_knock()
        # Should reset to 1 (the new knock)
        self.assertEqual(controller.knock_count, 1)

    @patch('security_gate.GunUI')
    @patch('security_gate.getpass.getpass')
    def test_trigger_gate_desktop_success(self, mock_getpass, MockGunUI):
        mock_getpass.return_value = config.DESKTOP_PASSWORD

        controller = AccessController(device_type="DESKTOP")

        # Knock REQUIRED_KNOCKS times
        for _ in range(config.REQUIRED_KNOCKS - 1):
            controller.process_knock()

        # The last knock triggers the gate
        controller.process_knock()

        self.assertEqual(controller.state, "AWAKENED")
        controller.ui.show_awakened.assert_called()

    @patch('security_gate.GunUI')
    @patch('security_gate.getpass.getpass')
    def test_trigger_gate_desktop_failure(self, mock_getpass, MockGunUI):
        mock_getpass.return_value = "WRONG_PASSWORD"

        controller = AccessController(device_type="DESKTOP")

        for _ in range(config.REQUIRED_KNOCKS):
            controller.process_knock()

        self.assertEqual(controller.state, "NIRODHA")
        controller.ui.show_access_denied.assert_called()
        self.assertEqual(controller.knock_count, 0)

    @patch('security_gate.GunUI')
    @patch('builtins.input')
    def test_trigger_gate_mobile_success(self, mock_input, MockGunUI):
        mock_input.return_value = config.MOBILE_PATTERN

        controller = AccessController(device_type="MOBILE")

        for _ in range(config.REQUIRED_KNOCKS):
            controller.process_knock()

        self.assertEqual(controller.state, "AWAKENED")

if __name__ == '__main__':
    unittest.main()
