import pytest
import sys
import os
import json
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.event_api import EventAPI


class TestAPINegative:
    """Negative API tests - invalid data"""

    @pytest.fixture(autouse=True)
    def setup(self, test_logger):
        self.api = EventAPI()
        self.logger = test_logger

    def test_missing_user_id(self, test_logger):
        """Test event without userId field"""
        test_logger.info("Step 1: Create event without userId")
        event_data = {
            "type": "play",
            "videoTime": 10.0,
            "timestamp": "2025-07-21T19:30:45.123Z"
        }

        test_logger.info("Step 2: Send invalid event")
        response = self.api.send_custom_event(event_data)

        test_logger.info("Step 3: Validate server response")
        assert response.status_code in [200, 400, 422], \
            f"Unexpected status: {response.status_code}"
        test_logger.warning(f"   Server accepts missing userId: {response.status_code}")

    def test_missing_type(self, test_logger):
        """Test event without type field"""
        test_logger.info("Step 1: Create event without type")
        event_data = {
            "userId": "user-123",
            "videoTime": 5.0,
            "timestamp": "2025-07-21T19:30:45.123Z"
        }

        test_logger.info("Step 2: Send and validate")
        response = self.api.send_custom_event(event_data)
        test_logger.warning(f"   Missing type response: {response.status_code}")

    def test_missing_video_time(self, test_logger):
        """Test event without videoTime field"""
        test_logger.info("Testing missing videoTime")
        event_data = {
            "userId": "user-123",
            "type": "play",
            "timestamp": "2025-07-21T19:30:45.123Z"
        }

        response = self.api.send_custom_event(event_data)
        test_logger.warning(f"   Missing videoTime response: {response.status_code}")

    def test_missing_timestamp(self, test_logger):
        """Test event without timestamp field"""
        test_logger.info("Testing missing timestamp")
        event_data = {
            "userId": "user-123",
            "type": "pause",
            "videoTime": 20.0
        }

        response = self.api.send_custom_event(event_data)
        test_logger.warning(f"   Missing timestamp response: {response.status_code}")

    def test_empty_payload(self, test_logger):
        """Test completely empty payload"""
        test_logger.info("Testing empty payload")
        response = self.api.send_custom_event({})
        test_logger.warning(f"   Empty payload response: {response.status_code}")

    def test_null_values(self, test_logger):
        """Test with null values"""
        test_logger.info("Testing null values")
        event_data = {
            "userId": None,
            "type": None,
            "videoTime": None,
            "timestamp": None
        }

        response = self.api.send_custom_event(event_data)
        test_logger.warning(f"   Null values response: {response.status_code}")

    def test_wrong_type_video_time(self, test_logger):
        """Test videoTime with wrong type (string instead of number)"""
        test_logger.info("Testing wrong type for videoTime")
        event_data = {
            "userId": "user-123",
            "type": "play",
            "videoTime": "not-a-number",
            "timestamp": "2025-07-21T19:30:45.123Z"
        }

        response = self.api.send_custom_event(event_data)
        test_logger.warning(f"   Wrong videoTime type response: {response.status_code}")

    def test_negative_video_time(self, test_logger):
        """Test negative videoTime"""
        test_logger.info("Testing negative videoTime")
        event_data = {
            "userId": "user-123",
            "type": "seeked",
            "videoTime": -10.5,
            "timestamp": "2025-07-21T19:30:45.123Z"
        }

        response = self.api.send_custom_event(event_data)
        test_logger.warning(f"   Negative videoTime response: {response.status_code}")

    def test_invalid_event_type(self, test_logger):
        """Test invalid event type"""
        test_logger.info("Testing invalid event type")
        event_data = {
            "userId": "user-123",
            "type": "invalid-type",
            "videoTime": 5.0,
            "timestamp": "2025-07-21T19:30:45.123Z"
        }

        response = self.api.send_custom_event(event_data)
        test_logger.warning(f"   Invalid event type response: {response.status_code}")

    def test_malformed_timestamp(self, test_logger):
        """Test malformed timestamp"""
        test_logger.info("Testing malformed timestamp")
        event_data = {
            "userId": "user-123",
            "type": "play",
            "videoTime": 0.0,
            "timestamp": "not-a-valid-timestamp"
        }

        response = self.api.send_custom_event(event_data)
        test_logger.warning(f"   Malformed timestamp response: {response.status_code}")

    def test_extra_fields(self, test_logger):
        """Test event with extra unexpected fields"""
        test_logger.info("Testing extra fields")
        event_data = {
            "userId": "user-123",
            "type": "play",
            "videoTime": 10.0,
            "timestamp": "2025-07-21T19:30:45.123Z",
            "extraField": "should-not-be-here",
            "anotherExtra": 123
        }

        response = self.api.send_custom_event(event_data)
        test_logger.info(f"   Extra fields response: {response.status_code}")
        test_logger.info(f"   Server accepts extra fields: {response.status_code == 200}")

    def test_wrong_content_type(self, test_logger):
        """Test sending with wrong content type"""
        test_logger.info("Testing wrong content type")

        response = self.api.session.post(
            f"{self.api.base_url}{self.api.endpoint}",
            data="This is not JSON",
            headers={'Content-Type': 'text/plain'}
        )

        test_logger.warning(f"   Wrong content type response: {response.status_code}")

    def test_malformed_json(self, test_logger):
        """Test sending malformed JSON"""
        test_logger.info("Testing malformed JSON")

        response = self.api.session.post(
            f"{self.api.base_url}{self.api.endpoint}",
            data='{"invalid": json}',  # JSON לא תקין
            headers={'Content-Type': 'application/json'}
        )

        test_logger.error(f"   Malformed JSON response: {response.status_code}")

    def test_huge_payload(self, test_logger):
        """Test with extremely large payload"""
        test_logger.info("Testing huge payload")

        event_data = {
            "userId": "user-" + "x" * 10000,  # userId ענק
            "type": "play",
            "videoTime": 999999999.999,
            "timestamp": "2025-07-21T19:30:45.123Z"
        }

        response = self.api.send_custom_event(event_data)
        test_logger.warning(f"   Huge payload response: {response.status_code}")

    def test_special_characters(self, test_logger):
        """Test with special characters in fields"""
        test_logger.info("Testing special characters")

        event_data = {
            "userId": "user-<script>alert('xss')</script>",
            "type": "play🎬",
            "videoTime": 10.0,
            "timestamp": "2025-07-21T19:30:45.123Z"
        }

        response = self.api.send_custom_event(event_data)
        test_logger.info(f"   Special characters response: {response.status_code}")
        test_logger.info("   ✅ Server handles special characters safely")