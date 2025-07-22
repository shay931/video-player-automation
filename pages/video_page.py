from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import datetime

class VideoPage():
    def __init__(self,driver):
        self.VIDEO = (By.ID, "video")
        self.driver = driver

        self.wait = WebDriverWait(self.driver, 10)



    def wait_for_video_ready(self):
        self.wait.until(
            EC.presence_of_element_located(self.VIDEO)
        )
        for i in range(10):
            ready = self.driver.execute_script(
                "return document.getElementById('video').readyState >= 2"
            )
            if ready:
                return
            time.sleep(0.5)

    def play_video(self):
        self.driver.execute_script("document.getElementById('video').play()")
        time.sleep(0.5)

    def pause_video(self):
        self.driver.execute_script("document.getElementById('video').pause()")
        time.sleep(0.5)

    def seek_video(self, seconds):
        self.driver.execute_script(f"document.getElementById('video').currentTime = {seconds}")
        time.sleep(0.5)

    def get_current_time(self):
        return self.driver.execute_script("return document.getElementById('video').currentTime")

    def get_duration(self):
        return self.driver.execute_script("return document.getElementById('video').duration")

    def is_playing(self):
        return self.driver.execute_script(
            "return !document.getElementById('video').paused && !document.getElementById('video').ended"
        )

    def is_paused(self):
        return self.driver.execute_script(
            "return document.getElementById('video').paused"
        )

    def add_scroll_content(self):
        """add content"""
        self.driver.execute_script("""
            const content = document.createElement('div');
            content.id = 'scroll-content';
            content.style.height = '2000px';
            content.innerHTML = '<h2>Scroll Test Content</h2>' + 
                               '<p>Lorem ipsum dolor sit amet...</p>'.repeat(50);
            document.body.appendChild(content);
        """)
        time.sleep(0.5)

    def scroll_to_position(self, y_position):
        """scroll to position"""
        self.driver.execute_script(f"window.scrollTo(0, {y_position})")
        time.sleep(0.5)

    def fail_with_screenshot(self, screenshot_name, logger):
        screenshots_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), "reports", "screenshots")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(screenshots_dir, f"{screenshot_name}_{timestamp}.png")
        self.driver.save_screenshot(path)
        logger.error(f"❌ 'failed'. Screenshot saved to: {path}")
        raise AssertionError(f"failed. Screenshot: {path}")



