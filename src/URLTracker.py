from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Logger import Logger
from typing import Union, List


class URLTracker:
    def __init__(self, driver: Union[webdriver.Edge, webdriver.Chrome, webdriver.Firefox]):
        self.__driver = driver
        self.__handles: List[str] = driver.window_handles.copy()
        self.__handleCount = len(self.__handles)

    def trackNewTabs(self):
        if self.__handleCount == len(self.__driver.window_handles):
            return

        currentHandles = set(self.__driver.window_handles)
        if len(currentHandles) > self.__handleCount:
            newHandles = currentHandles - set(self.__handles)
            for handle in newHandles:
                Logger.warn(f"New tab URL: {self.__driver.current_url}")
                self.__handles.append(handle)
        else:
            oldHandles = set(self.__handles) - currentHandles
            for handle in oldHandles:
                self.__handles.remove(handle)

    def save_html_content_of_current_page(self):
        WebDriverWait(self.__driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
