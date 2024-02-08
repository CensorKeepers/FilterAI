from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import time
from Logger import Logger

class URLTracker:
    def __init__(self, driver):
        self.driver = driver
        self.known_window_handles = set([driver.current_window_handle])  # Save the initially open window

    def track_new_tabs(self, duration=120, check_interval=10):
        start_time = time.time()
        while time.time() - start_time < duration:  # Continue the loop for the specified duration
            current_window_handles = set(self.driver.window_handles)
            new_window_handles = current_window_handles - self.known_window_handles

            for handle in new_window_handles:
                self.driver.switch_to.window(handle)
                Logger.warn(f"New tab URL: {self.driver.current_url}")
                self.save_html_content_of_current_page()
                self.known_window_handles.add(handle)         

            self.driver.switch_to.window(self.driver.current_window_handle) 
            sleep(check_interval) 


    def save_html_content_of_current_page(self):
        # Saves the HTML content of the current page to a file
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        html_content = self.driver.page_source
        print(html_content)
        print("-----------------------------------------------------------------")
            
