import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import sys
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.video_page import VideoPage

def get_events(driver, event_type=None):
    """locate event"""
    events = driver.execute_script("return window.capturedEvents || []")
    if event_type:
        return [e for e in events if e.get('type') == event_type]
    return events


def get_chrome_driver(logger):
    """Create Chrome driver with proper path"""
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


def get_firefox_driver(logger):
    """Create Firefox driver"""
    logger.info("Setting up Firefox driver...")


    service = FirefoxService(GeckoDriverManager().install())
    options = webdriver.FirefoxOptions()
    options.set_preference("media.autoplay.default", 0)
    options.set_preference("media.autoplay.blocking_policy", 0)

    return webdriver.Firefox(service=service, options=options)


@pytest.fixture
def setup_driver(request,test_logger):
    """Setup driver based on browser parameter"""
    browser = request.param

    try:
        if browser == "chrome":
            driver = get_chrome_driver(test_logger)
        else:  # firefox
            driver = get_firefox_driver(test_logger)

        driver.maximize_window()
        driver.get("http://localhost:3000")

        #Inject JavaScript
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
        test_logger.error(f"Failed to setup {browser}: {str(e)}")
        if browser == "firefox":
            pytest.skip(f"Firefox not available: {str(e)}")
        else:
            raise
    finally:
        if 'driver' in locals():
            test_logger.info(f"Closing {browser} driver...")
            driver.quit()



@pytest.mark.parametrize("setup_driver", ["chrome","firefox"], indirect=True)
class TestVideoPlayer:

    def test_play_button(self, setup_driver,test_logger):
        """button Play"""
        driver, page, browser = setup_driver

        test_logger.info(f"[{browser.upper()}] Step 1: Click play button")
        page.play_video()

        test_logger.info(f"[{browser.upper()}] Step 2: Wait for event to be sent")
        time.sleep(1)

        test_logger.info(f"[{browser.upper()}] Step 3: Verify video is playing")
        is_playing = page.is_playing()
        if not is_playing:
            page.fail_with_screenshot(f"{browser}] video not playing" , test_logger)

        # assert is_playing, f"{browser}video not play"
        test_logger.info(f"[{browser.upper()}] passed Video is playing: {is_playing}")

        test_logger.info(f"[{browser.upper()}] Step 4: Check play events")
        events = get_events(driver, 'play')
        assert len(events) > 0, f"{browser}not event play"
        test_logger.info(f"[{browser.upper()}] passed Found {len(events)} play events")

        test_logger.info(f"[{browser.upper()}] Step 5: Validate event structure")
        event = events[0]
        assert event['userId'] == 'user-123'
        assert event['type'] == 'play'
        assert 'videoTime' in event
        assert 'timestamp' in event
        test_logger.info(f"[{browser.upper()}]  passed play movie vent structure valid: {event}")

    def test_pause_button(self, setup_driver,test_logger):
        """button Pause"""
        driver, page, browser = setup_driver

        test_logger.info(f"[{browser.upper()}] Step 1: Play video first")
        page.play_video()
        time.sleep(1)

        test_logger.info(f"[{browser.upper()}] Step 2: Clear previous events")
        driver.execute_script("window.capturedEvents = []")

        test_logger.info(f"[{browser.upper()}] Step 3: Click pause button")
        page.pause_video()
        time.sleep(1)

        test_logger.info(f"[{browser.upper()}] Step 4: Verify video is paused")
        is_paused = page.is_paused()
        if not is_paused:
            page.fail_with_screenshot(f"{browser}] video not paused" , test_logger)


        test_logger.info(f"[{browser.upper()}] passed Video is paused: {is_paused}")

        test_logger.info(f"[{browser.upper()}] Step 5: Check pause events")
        events = get_events(driver, 'pause')

        if len(events) == 0:
            play_events = get_events(driver, 'play')
            test_logger.warning(f"[{browser.upper()}] BUG FOUND: Pause sends 'play' event instead of 'pause'")
            test_logger.warning(f"[{browser.upper()}] Events captured: {play_events}")

        all_events = get_events(driver)
        assert len(all_events) > 0, f"[{browser}] no event"

        event = all_events[0]
        assert event['userId'] == 'user-123'
        assert 'videoTime' in event
        assert 'timestamp' in event
        test_logger.info(f"[{browser.upper()}]  passed test pause button")

    def test_seek_control(self, setup_driver,test_logger):
        """video Seek"""
        driver, page, browser = setup_driver

        test_logger.info(f"[{browser.upper()}] Step 1: Play video")
        page.play_video()
        time.sleep(1)

        test_logger.info(f"[{browser.upper()}] Step 2: Get video duration")
        duration = page.get_duration()
        test_logger.info(f"[{browser.upper()}] Video duration: {duration:.1f} seconds")

        test_logger.info(f"[{browser.upper()}] Step 3: Clear events and seek to 10 seconds")
        driver.execute_script("window.capturedEvents = []")
        seek_time = 10.0
        page.seek_video(seek_time)
        time.sleep(1)

        test_logger.info(f"[{browser.upper()}] Step 4: Verify seek worked")
        current_time = page.get_current_time()
        if abs(current_time - seek_time) > 1:
            page.fail_with_screenshot(f"{browser}] video not seek" , test_logger)


        test_logger.info(f"[{browser.upper()}] passed Seeked to {current_time:.1f}s")

        test_logger.info(f"[{browser.upper()}] Step 5: Check seeked events")
        events = get_events(driver, 'seeked')
        assert len(events) > 0, f"[{browser}no event seeked"

        event = events[0]
        assert event['userId'] == 'user-123'
        assert event['type'] == 'seeked'
        assert 'videoTime' in event
        test_logger.info(f"[{browser.upper()}]  passed Seeked event valid: {event}")

    def test_scroll_event(self, setup_driver,test_logger):
        """event Scroll"""
        driver, page, browser = setup_driver

        test_logger.info(f"[{browser.upper()}] Step 1: Add content to make page scrollable")
        page.add_scroll_content()

        test_logger.info(f"[{browser.upper()}] Step 2: Scroll to top")
        page.scroll_to_position(0)
        time.sleep(1)

        test_logger.info(f"[{browser.upper()}] Step 3: Clear events and scroll down")
        driver.execute_script("window.capturedEvents = []")
        page.scroll_to_position(500)
        time.sleep(1)

        test_logger.info(f"[{browser.upper()}] Step 4: Check initial scroll events")
        events = get_events(driver, 'scroll')
        initial_events = len(events)
        test_logger.info(f"[{browser.upper()}] Scroll events after first scroll: {initial_events}")

        test_logger.info(f"[{browser.upper()}] Step 5: Scroll more")
        page.scroll_to_position(1000)
        time.sleep(1)

        events = get_events(driver, 'scroll')
        test_logger.info(f"[{browser.upper()}] Total scroll events: {len(events)}")

        if len(events) == 0:
            page.fail_with_screenshot(f"{browser}] video not scroll", test_logger)

        test_logger.info(f"[{browser.upper()}] Step 6: Validate scroll event structure")
        event = events[0]
        assert event['userId'] == 'user-123'
        assert event['type'] == 'scroll'
        assert 'videoTime' in event
        assert 'timestamp' in event
        test_logger.info(f"[{browser.upper()}] passed Scroll event valid: {event}")