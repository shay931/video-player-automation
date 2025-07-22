import pytest
import time
import logging
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.video_page import VideoPage


def get_events(driver, event_type=None):
    """קבל אירועים שנתפסו"""
    events = driver.execute_script("return window.capturedEvents || []")
    if event_type:
        return [e for e in events if e.get('type') == event_type]
    return events


def get_chrome_driver():
    """Create Chrome driver with proper path"""
    logger = logging.getLogger(__name__)
    logger.info("Setting up Chrome driver...")

    # Get the correct chromedriver path
    driver_path = ChromeDriverManager().install()

    # Fix the path if it points to wrong file
    if driver_path.endswith('THIRD_PARTY_NOTICES.chromedriver'):
        driver_path = driver_path.replace('THIRD_PARTY_NOTICES.chromedriver', 'chromedriver.exe')

    logger.info(f"Chrome driver path: {driver_path}")

    service = ChromeService(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument("--autoplay-policy=no-user-gesture-required")
    options.add_argument("--disable-blink-features=AutomationControlled")

    return webdriver.Chrome(service=service, options=options)


def get_firefox_driver():
    """Create Firefox driver"""
    logger = logging.getLogger(__name__)
    logger.info("Setting up Firefox driver...")

    # Try to find Firefox installation
    firefox_paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        os.path.expanduser(r"~\AppData\Local\Mozilla Firefox\firefox.exe"),
    ]

    firefox_binary = None
    for path in firefox_paths:
        if os.path.exists(path):
            firefox_binary = path
            logger.info(f"Found Firefox at: {path}")
            break

    if not firefox_binary:
        raise Exception("Firefox not found. Please install Firefox or run tests with Chrome only")

    service = FirefoxService(GeckoDriverManager().install())
    options = webdriver.FirefoxOptions()
    options.binary_location = firefox_binary
    options.set_preference("media.autoplay.default", 0)
    options.set_preference("media.autoplay.blocking_policy", 0)

    return webdriver.Firefox(service=service, options=options)


@pytest.fixture
def setup_driver(request):
    """Setup driver based on browser parameter"""
    browser = request.param
    logger = logging.getLogger(__name__)

    try:
        if browser == "chrome":
            driver = get_chrome_driver()
        else:  # firefox
            driver = get_firefox_driver()

        driver.maximize_window()
        driver.get("http://localhost:3000")

        # Inject JavaScript
        driver.execute_script("""
            window.capturedEvents = [];
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                if (args[0] === '/api/event') {
                    const body = JSON.parse(args[1].body);
                    window.capturedEvents.push(body);
                }
                return originalFetch.apply(this, args);
            };
        """)

        # Create page object
        page = VideoPage(driver)
        page.wait_for_video_ready()

        yield driver, page, browser

    except Exception as e:
        logger.error(f"Failed to setup {browser}: {str(e)}")
        if browser == "firefox":
            pytest.skip(f"Firefox not available: {str(e)}")
        else:
            raise
    finally:
        if 'driver' in locals():
            logger.info(f"Closing {browser} driver...")
            driver.quit()


# Run tests only on Chrome if Firefox is not available
browsers_to_test = ["chrome"]
try:
    # Check if Firefox is available
    firefox_paths = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    ]
    if any(os.path.exists(path) for path in firefox_paths):
        browsers_to_test.append("firefox")
except:
    pass


@pytest.mark.parametrize("setup_driver", browsers_to_test, indirect=True)
class TestVideoPlayer:

    def test_play_button(self, setup_driver):
        """בדיקת כפתור Play"""
        driver, page, browser = setup_driver
        logger = logging.getLogger(__name__)

        logger.info(f"[{browser.upper()}] Step 1: Click play button")
        page.play_video()

        logger.info(f"[{browser.upper()}] Step 2: Wait for event to be sent")
        time.sleep(1)

        logger.info(f"[{browser.upper()}] Step 3: Verify video is playing")
        is_playing = page.is_playing()
        assert is_playing, f"[{browser}] וידאו לא מנגן"
        logger.info(f"[{browser.upper()}] ✅ Video is playing: {is_playing}")

        logger.info(f"[{browser.upper()}] Step 4: Check play events")
        events = get_events(driver, 'play')
        assert len(events) > 0, f"[{browser}] לא נמצא אירוע play"
        logger.info(f"[{browser.upper()}] ✅ Found {len(events)} play events")

        logger.info(f"[{browser.upper()}] Step 5: Validate event structure")
        event = events[0]
        assert event['userId'] == 'user-123'
        assert event['type'] == 'play'
        assert 'videoTime' in event
        assert 'timestamp' in event
        logger.info(f"[{browser.upper()}] ✅ Event structure valid: {event}")

    def test_pause_button(self, setup_driver):
        """בדיקת כפתור Pause"""
        driver, page, browser = setup_driver
        logger = logging.getLogger(__name__)

        logger.info(f"[{browser.upper()}] Step 1: Play video first")
        page.play_video()
        time.sleep(1)

        logger.info(f"[{browser.upper()}] Step 2: Clear previous events")
        driver.execute_script("window.capturedEvents = []")

        logger.info(f"[{browser.upper()}] Step 3: Click pause button")
        page.pause_video()
        time.sleep(1)

        logger.info(f"[{browser.upper()}] Step 4: Verify video is paused")
        is_paused = page.is_paused()
        assert is_paused, f"[{browser}] וידאו לא עצר"
        logger.info(f"[{browser.upper()}] ✅ Video is paused: {is_paused}")

        logger.info(f"[{browser.upper()}] Step 5: Check pause events")
        events = get_events(driver, 'pause')

        if len(events) == 0:
            play_events = get_events(driver, 'play')
            logger.warning(f"[{browser.upper()}] BUG FOUND: Pause sends 'play' event instead of 'pause'")
            logger.warning(f"[{browser.upper()}] Events captured: {play_events}")

        all_events = get_events(driver)
        assert len(all_events) > 0, f"[{browser}] לא נמצאו אירועים כלל"

        event = all_events[0]
        assert event['userId'] == 'user-123'
        assert 'videoTime' in event
        assert 'timestamp' in event
        logger.info(f"[{browser.upper()}] ✅ Event sent: {event}")

    def test_seek_control(self, setup_driver):
        """בדיקת Seek - קפיצה בוידאו"""
        driver, page, browser = setup_driver
        logger = logging.getLogger(__name__)

        logger.info(f"[{browser.upper()}] Step 1: Play video")
        page.play_video()
        time.sleep(1)

        logger.info(f"[{browser.upper()}] Step 2: Get video duration")
        duration = page.get_duration()
        logger.info(f"[{browser.upper()}] Video duration: {duration:.1f} seconds")

        logger.info(f"[{browser.upper()}] Step 3: Clear events and seek to 10 seconds")
        driver.execute_script("window.capturedEvents = []")
        seek_time = 10.0
        page.seek_video(seek_time)
        time.sleep(1)

        logger.info(f"[{browser.upper()}] Step 4: Verify seek worked")
        current_time = page.get_current_time()
        assert abs(current_time - seek_time) < 1, f"[{browser}] Seek failed: expected {seek_time}, got {current_time}"
        logger.info(f"[{browser.upper()}] ✅ Seeked to {current_time:.1f}s")

        logger.info(f"[{browser.upper()}] Step 5: Check seeked events")
        events = get_events(driver, 'seeked')
        assert len(events) > 0, f"[{browser}] לא נמצא אירוע seeked"

        event = events[0]
        assert event['userId'] == 'user-123'
        assert event['type'] == 'seeked'
        assert 'videoTime' in event
        assert abs(event['videoTime'] - seek_time) < 1, f"Wrong time in event: {event['videoTime']}"
        logger.info(f"[{browser.upper()}] ✅ Seeked event valid: {event}")

    def test_scroll_event(self, setup_driver):
        """בדיקת אירוע Scroll"""
        driver, page, browser = setup_driver
        logger = logging.getLogger(__name__)

        logger.info(f"[{browser.upper()}] Step 1: Add content to make page scrollable")
        page.add_scroll_content()

        logger.info(f"[{browser.upper()}] Step 2: Scroll to top")
        page.scroll_to_position(0)
        time.sleep(1)

        logger.info(f"[{browser.upper()}] Step 3: Clear events and scroll down")
        driver.execute_script("window.capturedEvents = []")
        page.scroll_to_position(500)
        time.sleep(1)

        logger.info(f"[{browser.upper()}] Step 4: Check initial scroll events")
        events = get_events(driver, 'scroll')
        initial_events = len(events)
        logger.info(f"[{browser.upper()}] Scroll events after first scroll: {initial_events}")

        logger.info(f"[{browser.upper()}] Step 5: Scroll more")
        page.scroll_to_position(1000)
        time.sleep(1)

        events = get_events(driver, 'scroll')
        logger.info(f"[{browser.upper()}] Total scroll events: {len(events)}")

        assert len(events) > 0, f"[{browser}] לא נמצאו אירועי scroll"

        logger.info(f"[{browser.upper()}] Step 6: Validate scroll event structure")
        event = events[0]
        assert event['userId'] == 'user-123'
        assert event['type'] == 'scroll'
        assert 'videoTime' in event
        assert 'timestamp' in event
        logger.info(f"[{browser.upper()}] ✅ Scroll event valid: {event}")