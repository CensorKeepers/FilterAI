from selenium import webdriver

from typing import Union, List, Dict

from Logger import Logger
from ContentFetcher import ContentFetcher

'''
url değişikliğini bulmak
tab acilip kapandiysa bunu fark edip onlari listeye eklemek cikarmak
html contentleri alirken refresh kontrol et
html'leri al
'''


class URLTracker:
    def __init__(self, driver: Union[webdriver.Edge, webdriver.Chrome, webdriver.Firefox]):
        self.__driver = driver
        self.__handles: Dict[str, str] = {}
        self.__updateHandlesAndUrls()
        self.__contentFetcher = ContentFetcher(self.__driver)
        self.__lastActiveHandle = self.__driver.current_window_handle

    def __updateHandlesAndUrls(self, currentHandles=None):
        if currentHandles is None:
            currentHandles = self.__driver.window_handles
        updated_handles = {}

        for handle in currentHandles:
            self.__driver.switch_to.window(handle)
            url = self.__driver.current_url
            updated_handles[handle] = url

        self.__handles = updated_handles

    def trackUrls(self):
        try:
            currentHandles = self.__driver.window_handles
            activeHandle = self.__driver.current_window_handle
        except:
            return

        if set(currentHandles) != set(self.__handles):
            self.__updateHandlesAndUrls(currentHandles)

        if activeHandle != self.__lastActiveHandle:
            # Logger.warn(f"Kullanici {self.__lastActiveHandle} sekmesinden {activeHandle} sekmesine gecti")
            self.__lastActiveHandle = activeHandle
            self.__driver.switch_to.window(self.__lastActiveHandle)

        current_url = self.__driver.current_url
        if self.__handles[activeHandle] != current_url:
            # Logger.warn(f"URL changed in {activeHandle} from {self.__handles[activeHandle]} to {current_url}")
            self.__handles[activeHandle] = current_url

        self.__trackHtmlContentsOfUrls()

    def __trackHtmlContentsOfUrls(self):
        handles = dict(self.__handles)
        self.__contentFetcher.fetchAndPrintHtmlContents(handles)
