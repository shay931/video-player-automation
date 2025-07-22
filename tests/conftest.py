import pytest
import logging
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.video_page import VideoPage

# Setup directories
os.makedirs("reports/logs", exist_ok=True)
os.makedirs("reports/screenshots", exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@pytest.fixture(params=["chrome", "firefox"])
def browser(request):
    """Browser parameter"""
    return request.param


@pytest.fixture
def driver(browser):
    """Create WebDriver for browser"""
    logger.info(f"Starting {browser} driver...")

    if browser == "chrome":
        service = ChromeService(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--autoplay-policy=no-user-gesture-required")
        driver = webdriver.Chrome(service=service, options=options)
    else:  # firefox
        service = FirefoxService(GeckoDriverManager().install())
        options = webdriver.FirefoxOptions()
        options.set_preference("media.autoplay.default", 0)
        driver = webdriver.Firefox(service=service, options=options)

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

    yield driver
    driver.quit()


@pytest.fixture
def page(driver):
    return VideoPage(driver)


@pytest.fixture
def test_logger():
    return logger