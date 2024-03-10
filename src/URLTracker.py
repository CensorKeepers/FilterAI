from selenium import webdriver

from typing import Union, List, Dict

from Logger import Logger
from ContentFetcher import ContentFetcher
from JSHandler import JSHandler

'''
url değişikliğini bulmak
tab acilip kapandiysa bunu fark edip onlari listeye eklemek cikarmak
html contentleri alirken refresh kontrol et
html'leri al
'''


class URLTracker:
    def __init__(self, driver: Union[webdriver.Edge, webdriver.Chrome, webdriver.Firefox]):
        self.__driver = driver
        self.__handle: str = ''
        self.__url: str = ''
        self.__contentFetcher = ContentFetcher(self.__driver)
        self.__jsHandler = JSHandler(self.__driver)
        self.__initializeHandlesAndUrls()

    def __initializeHandlesAndUrls(self):
        self.__handle = self.__driver.current_window_handle
        self.__url = self.__driver.current_url

    def trackUrls(self):
        # Driver açık mı değil mi diye kontrol.
        # Sekmeleri kapatınca gelen hatanın sebebi de bu.
        try:
            self.__driver.current_window_handle
        except:
            return

        self.__removeOtherTabs()
        # self.__trackHtmlContentsOfUrls()

    def __removeOtherTabs(self) -> None:
        handles = self.__driver.window_handles
        if len(handles) > 1:
            handlesToBeRemoved = set(handles) - set([self.__handle])
            for handle in handlesToBeRemoved:
                self.__driver.switch_to.window(handle)
                self.__driver.close()
            self.__driver.switch_to.window(self.__handle)
            self.__jsHandler.makeAlert('Only one tab is allowed.')

    def __trackHtmlContentsOfUrls(self):
        self.__contentFetcher.fetchAndPrintHtmlContents(self.__handle)
