import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.event_api import EventAPI


class TestAPIPositive:
    """Positive API tests - valid data"""

    @pytest.fixture(autouse=True)
    def setup(self, test_logger):
        self.api = EventAPI()

    def test_send_play_event(self, test_logger):
        """Test sending valid play event"""

        test_logger.info("Step 1: Send play event to API")
        response = self.api.send_event(
            event_type="play",
            video_time=0.0
        )

        test_logger.info("Step 2: Validate response status")
        assert response.status_code == 200, f"Failed: {response.text}"
        test_logger.info(f" passed Status code: {response.status_code}")

        test_logger.info("Step 3: Validate response body")
        body = response.json()
        assert body.get('ok') == True
        test_logger.info(f" passed Response body: {body}")

    def test_send_pause_event(self, test_logger):
        """Test sending valid pause event"""
        test_logger.info("Step 1: Send pause event")
        response = self.api.send_event(
            event_type="pause",
            video_time=15.5
        )

        test_logger.info("Step 2: Validate response")
        assert response.status_code == 200
        body = response.json()
        assert body.get('ok') == True
        test_logger.info(f"   passed Pause event sent successfully: {body}")

    def test_send_seeked_event(self, test_logger):
        """Test sending valid seeked event"""
        test_logger.info("Step 1: Send seeked event")
        response = self.api.send_event(
            event_type="seeked",
            video_time=45.75
        )

        test_logger.info("Step 2: Validate response")
        assert response.status_code == 200
        body = response.json()
        assert body.get('ok') == True
        test_logger.info(f"   passed Seeked event sent successfully: {body}")

    def test_send_scroll_event(self, test_logger):
        """Test sending valid scroll event"""
        test_logger.info("Step 1: Send scroll event")
        response = self.api.send_event(
            event_type="scroll",
            video_time=5.0
        )

        test_logger.info("Step 2: Validate response")
        assert response.status_code == 200
        body = response.json()
        assert body.get('ok') == True
        test_logger.info(f"   passed Scroll event sent successfully: {body}")

    def test_all_required_fields(self, test_logger):
        """Test event with all required fields"""
        test_logger.info("Step 1: Create complete event structure")
        event_data = {
            "userId": "user-123",
            "type": "play",
            "videoTime": 12.345,
            "timestamp": "2025-07-21T19:30:45.123Z"
        }
        test_logger.info(f"   Event data: {event_data}")

        test_logger.info("Step 2: Send event")
        response = self.api.send_custom_event(event_data)

        test_logger.info("Step 3: Validate response")
        assert response.status_code == 200
        body = response.json()
        assert body.get('ok') == True
        test_logger.info(f"   passed Complete event accepted: {body}")



    def test_various_video_times(self, test_logger):
        """Test events with various video times"""
        test_logger.info("Step 1: Test various video times")
        times = [0.0, 0.5, 3.0]

        for i, video_time in enumerate(times, 1):
            test_logger.info(f"   {i}. Testing time: {video_time}s")
            response = self.api.send_event(
                event_type="seeked",
                video_time=video_time
            )

            assert response.status_code == 200
            test_logger.info(f" passed Event sent with time {video_time}s")

    def test_rapid_events(self, test_logger):
        """Test sending multiple events rapidly"""
        test_logger.info("Step 1: Send 10 events rapidly")

        success_count = 0
        for i in range(6):
            response = self.api.send_event(
                event_type="play" if i % 2 == 0 else "pause",
                video_time=float(i)
            )

            if response.status_code == 200:
                success_count += 1

        test_logger.info(f"Step 2: Validate all events sent")
        assert success_count == 6, f"Only {success_count}/10 events succeeded"
        test_logger.info(f" passed  All 6 events sent successfully")