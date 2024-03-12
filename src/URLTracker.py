from selenium import webdriver
import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Union, List
from time import sleep
from Logger import Logger
import threading
from ContentFetcher import ContentFetcher     
from selenium.common.exceptions import NoSuchWindowException    

class URLTracker:
    def __init__(self, driver):
        self.__driver = driver
        self.__handles = {}  
        self.__handles.update({handle: self.__driver.current_url for handle in driver.window_handles})
        self._handleCount = len(self.__handles)
        self.__updateHandlesAndUrls()
        self.__contentFetcher = ContentFetcher(self.__driver)
        self.__lastActiveHandle = ""


    def trackUrls(self):
        try:
            currentHandles = self.__driver.window_handles
            original_handle = self.__driver.current_window_handle

            if set(currentHandles) != set(self.__handles.keys()):            
                self.__updateHandlesAndUrls(currentHandles)
            else:
                if original_handle != self.__lastActiveHandle:
                    Logger.warn(f"Kullanici {self.__lastActiveHandle} sekmesinden {original_handle} sekmesine gecti")
                    self.__lastActiveHandle = original_handle
                    self.__driver.switch_to.window(original_handle)

                current_url = self.__driver.current_url
                if self.__handles[original_handle] != current_url:
                    Logger.warn(f"URL changed in {original_handle} from {self.__handles[original_handle]} to {current_url}")
                    self.__handles[original_handle] = current_url
        except NoSuchWindowException:
            #Logger.error("Bir pencere/sekmeye erişilemiyor.")
            self.__handleWindowClosedScenario()
        self.__trackHtmlContentsOfUrls()
    
    
    def __updateHandlesAndUrls(self, currentHandles=None):
        try:
            if currentHandles is None:
                currentHandles = self.__driver.window_handles

            currentHandlesSet = set(currentHandles)
            existingHandlesSet = set(self.__handles.keys())

            closedHandles = existingHandlesSet - currentHandlesSet
            newHandles = currentHandlesSet - existingHandlesSet

            for handle in closedHandles:
                self.__deleteClosedTabHtmlContent(handle)
                del self.__handles[handle]     

            for handle in newHandles:
                self.__driver.switch_to.window(handle)
                url = self.__driver.current_url
                self.__handles[handle] = url

            if self.__driver.current_window_handle in currentHandles:
                self.__driver.switch_to.window(self.__driver.current_window_handle)

            self._handleCount = len(self.__handles)
        except NoSuchWindowException:
            self.__handleWindowClosedScenario()
            
    def __handleWindowClosedScenario(self):
        currentHandles = self.__driver.window_handles
        if currentHandles:
            self.__driver.switch_to.window(currentHandles[0])
            self.__lastActiveHandle = currentHandles[0]
            Logger.warn("Switched to a remaining window after the current window was closed.")
        else:
            Logger.error("No remaining windows to switch to. Program is stopping.")
            self.__stopProgram()

    def __stopProgram(self):
        self.__driver.quit()
        Logger.info("Program has been successfully stopped.")


    def __trackHtmlContentsOfUrls(self):
        handlesDict = dict(self.__handles)
        currentHandle = self.__driver.current_window_handle
        self.__contentFetcher.fetchAndPrintHtmlContents(handlesDict, currentHandle)
        
    def __deleteClosedTabHtmlContent(self, deletedTab):
        self.__contentFetcher.deleteFiles(deletedTab)
