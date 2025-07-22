from datetime import datetime
import requests


class EventAPI():
    """API class for event endpoint"""

    def __init__(self,base_url="http://localhost:3000"):
        super().__init__()
        self.endpoint = "/api/event"
        self.base_url = base_url
        self.session = requests.Session()

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

    def post(self, endpoint, data=None, **kwargs):
        """Send POST request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data, **kwargs)
        return response



