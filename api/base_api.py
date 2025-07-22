import requests
import json
from datetime import datetime


class BaseAPI:
    """Base class for API testing"""

    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })

    def post(self, endpoint, data=None, **kwargs):
        """Send POST request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data, **kwargs)
        return response

    def get(self, endpoint, **kwargs):
        """Send GET request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, **kwargs)
        return response

    def log_request(self, method, url, data=None):
        """Log request details"""
        print(f"\n📤 {method} {url}")
        if data:
            print(f"   Body: {json.dumps(data, indent=2)}")

    def log_response(self, response):
        """Log response details"""
        print(f"📥 Status: {response.status_code}")
        try:
            print(f"   Body: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"   Body: {response.text}")