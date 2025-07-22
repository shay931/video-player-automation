from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.base_page import BasePage


class VideoPage(BasePage):
    VIDEO = (By.ID, "video")

    def load(self):
        # כבר נטען ב-conftest
        self.wait_for_video_ready()

    def wait_for_video_ready(self):
        """חכה שהוידאו יהיה מוכן"""
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.VIDEO)
        )
        # חכה שהוידאו יטען
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
        """הוסף תוכן כדי שיהיה אפשר לגלול"""
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
        """גלול למיקום מסוים"""
        self.driver.execute_script(f"window.scrollTo(0, {y_position})")
        time.sleep(0.5)

    def scroll_to_video(self):
        """גלול עד שהוידאו נראה"""
        self.driver.execute_script(
            "document.getElementById('video').scrollIntoView()"
        )
        time.sleep(0.5)

    def get_scroll_position(self):
        """קבל מיקום גלילה נוכחי"""
        return self.driver.execute_script("return window.pageYOffset")