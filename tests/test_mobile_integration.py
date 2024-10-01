import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure the core directory is accessible for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))

from mobile_integration import MobileIntegration  # Import MobileIntegration class

class TestMobileIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up the MobileIntegration instance before each test."""
        self.mobile_integration = MobileIntegration()

    def test_initialize_google_credentials(self):
        """Test initialization of Google credentials."""
        # Mock the behavior of the credentials loading
        with patch('google.oauth2.credentials.Credentials.from_authorized_user_file') as mock_credentials:
            mock_credentials.return_value = MagicMock()
            credentials = self.mobile_integration.initialize_google_credentials()
            self.assertIsNotNone(credentials)  # Check that credentials are not None

        # Test with a missing file scenario
        with patch('google.oauth2.credentials.Credentials.from_authorized_user_file', side_effect=FileNotFoundError):
            credentials = self.mobile_integration.initialize_google_credentials()
            self.assertIsNone(credentials)  # Check that credentials are None if file is not found

    def test_check_travel_patterns(self):
        """Test the check_travel_patterns method."""
        # Mock the Google API build function and events list
        with patch('googleapiclient.discovery.build') as mock_build:
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            mock_service.events().list().execute.return_value = {
                'items': [{'summary': 'Meeting with Team'}, {'summary': 'Doctor Appointment'}]
            }

            self.mobile_integration.check_travel_patterns()
            mock_service.events().list.assert_called_once()  # Ensure the events list was called

    def test_listen_for_requests(self):
        """Test the listen_for_requests method."""
        response = self.mobile_integration.listen_for_requests()
        self.assertEqual(response, "Check my schedule")  # Check the response string

    def test_respond(self):
        """Test the respond method (placeholder)."""
        try:
            self.mobile_integration.respond("Test response")
            self.assertTrue(True)  # Check that no exceptions were raised
        except Exception as e:
            self.fail(f"respond method raised an exception: {e}")

if __name__ == "__main__":
    unittest.main()
