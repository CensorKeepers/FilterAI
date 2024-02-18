from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from typing import Union, List
import time
from time import sleep
from Logger import Logger
import threading
from ContentFetcher import ContentFetcher     
     
#source .venv/Scripts/activate
#cd src/
#python main.py
#firefox --marionette
class URLTracker:
    def __init__(self, driver: Union[webdriver.Edge, webdriver.Chrome, webdriver.Firefox]):
        self.__driver = driver
        self.__handles: List[str] = driver.window_handles.copy()
        self.__handleCount = len(self.__handles)
        self.__thread = threading.Thread(target=self.__process, args=())
        self.__refreshThread = threading.Thread(target=self.__handleRefreshs, args=())
        self.__updateHandlesAndUrls()
        self.__contentFetcher = ContentFetcher(self.__driver)
        self.__contentFetcher.reset()
        
    def trackUrls(self):
        currentHandles = self.__driver.window_handles
        if set(currentHandles) != set(self.__handles.keys()):
            self.__updateHandlesAndUrls(currentHandles)
            self.__trackHtmlContentsOfUrls()

    def __updateHandlesAndUrls(self, currentHandles=None):
        if currentHandles is None:
            currentHandles = self.__driver.window_handles
        updated_handles = {}
        
        for handle in currentHandles:
            self.__driver.switch_to.window(handle)
            url = self.__driver.current_url
            updated_handles[handle] = url
        
        self.__handles = updated_handles
        self.__handleCount = len(self.__handles)
        # Orijinal sekme uzerinde kalabilmek icin
        if self.__driver.current_window_handle in currentHandles:
            self.__driver.switch_to.window(self.__driver.current_window_handle)

    def __trackHtmlContentsOfUrls(self):
        handles_dict = dict(self.__handles)
        self.__contentFetcher.fetchAndPrintHtmlContents(handles_dict)
        
    def __getCurrentUrls(self):
        return list(self.__handles.values())
    
    def __printCurrentTabsAndUrls(self):
        print("Aktif Sekmeler ve URL'leri:")
        for handle, url in self.__handles.items():
            print(f"Sekme: {handle}, URL: {url}")

    def __process(self) -> None:
        self.__refreshThread.start()
        self.__refreshThread.join()

    def start(self) -> None:
        self.__thread.start()

    def join(self) -> None:
        self.__thread.join()
    
    def __handleRefreshs(self) -> None:
        while self.__handleCount != 0:
            sleep(0.1)
