from selenium import webdriver
from selenium.common.exceptions import NoSuchWindowException
from typing import Union

from Logger import Logger
from ContentFetcher import ContentFetcher
from JSHandler import JSHandler


class URLTracker:
    def __init__(self, driver: Union[webdriver.Firefox, webdriver.Edge, webdriver.Chrome]):
        self.__driver = driver
        self.__handleUrlPairs = {}
        self.__contentFetcher = ContentFetcher(self.__driver)
        self.__jsHandler = JSHandler(self.__driver)
        self.__lastActiveHandle = self.__driver.current_window_handle
        self.__updateHandlesAndUrls()

    def trackUrls(self):
        try:
            currentHandles = self.__driver.window_handles
            activeHandle = self.__driver.current_window_handle
        except:
            self.__handleWindowClosedScenario()

        if set(currentHandles) != set(self.__handleUrlPairs):
            self.__updateHandlesAndUrls()

        # if activeHandle != self.__lastActiveHandle:
        #    Logger.warn(f"Kullanici {self.__lastActiveHandle} sekmesinden {activeHandle} sekmesine gecti")
        #    self.__lastActiveHandle = activeHandle
        #    self.__driver.switch_to.window(activeHandle)

        current_url = self.__driver.current_url
        if self.__handleUrlPairs[activeHandle] != current_url:
            Logger.warn(f"[URL]: URL changed in {activeHandle} from {self.__handleUrlPairs[activeHandle]} to {current_url}")
            self.__handleUrlPairs[activeHandle] = current_url
            self.__jsHandler.initialEmbeddings()

        elif self.__jsHandler.isPageRefreshed():
            Logger.warn(f'[REFRESH]: Tab "{activeHandle}", URL "{self.__handleUrlPairs[activeHandle]}" has been refreshed!')
            self.__jsHandler.initialEmbeddings()

        self.__trackHtmlContentsOfUrls()

    def __updateHandlesAndUrls(self):
        try:
            driverHandles = set(self.__driver.window_handles.copy())
            localHandles = set(self.__handleUrlPairs)

            closedHandles = localHandles - driverHandles
            newHandles = driverHandles - localHandles

            for handle in closedHandles:
                self.__deleteClosedTabHtmlContent(handle)
                del self.__handleUrlPairs[handle]

            for handle in newHandles:
                self.__driver.switch_to.window(handle)
                url = self.__driver.current_url
                self.__handleUrlPairs[handle] = url
                self.__jsHandler.initialEmbeddings()

        except NoSuchWindowException:
            self.__handleWindowClosedScenario()

    def __trackHtmlContentsOfUrls(self):
        handlesDict = dict(self.__handleUrlPairs)
        currentHandle = self.__driver.current_window_handle
        self.__contentFetcher.fetchAndPrintHtmlContents(handlesDict, currentHandle, self.__jsHandler)

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

    def __deleteClosedTabHtmlContent(self, deletedTab):
        self.__contentFetcher.deleteFiles(deletedTab)
