from datetime import datetime
from api.base_api import BaseAPI


class EventAPI(BaseAPI):
    """API class for event endpoint"""

    def __init__(self):
        super().__init__()
        self.endpoint = "/api/event"

    def send_event(self, event_type, video_time=0.0, user_id="user-123", timestamp=None):
        """Send event to API"""
        if timestamp is None:
            timestamp = datetime.now().isoformat() + 'Z'

        data = {
            "userId": user_id,
            "type": event_type,
            "videoTime": video_time,
            "timestamp": timestamp
        }

        response = self.post(self.endpoint, data)
        return response

    def send_custom_event(self, data):
        """Send custom event data"""
        response = self.post(self.endpoint, data)
        return response

    def validate_response(self, response, expected_status=200):
        """Validate API response"""
        assert response.status_code == expected_status, \
            f"Expected status {expected_status}, got {response.status_code}"

        # בדוק שיש response body
        try:
            body = response.json()
            return body
        except:
            return None

    def create_valid_event(self, event_type="play", video_time=10.5):
        """Create valid event data"""
        return {
            "userId": "user-123",
            "type": event_type,
            "videoTime": video_time,
            "timestamp": datetime.now().isoformat() + 'Z'
        }