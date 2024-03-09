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
        self.__handleUrlPairs: Dict[str, str] = {}
        self.__jsHandler = JSHandler(self.__driver)
        self.__contentFetcher = ContentFetcher(self.__driver)
        self.__initializeHandlesAndUrls()

    def __initializeHandlesAndUrls(self):
        initialHandles = self.__driver.window_handles.copy()
        self.__jsHandler.deleteLocalStorage()

        for handle in initialHandles:
            self.__driver.switch_to.window(handle)
            url = self.__driver.current_url
            self.__handleUrlPairs[handle] = url
            self.__jsHandler.initialEmbeddings()

        self.__jsHandler.setLocalStorageToActiveHandle()

    def trackUrls(self):
        # Driver açık mı değil mi diye kontrol.
        # Sekmeleri kapatınca gelen hatanın sebebi de bu.
        try:
            self.__driver.current_window_handle
        except:
            return

        self.__updateHandlesAndUrls()
        self.__trackHtmlContentsOfUrls()

    def __updateHandlesAndUrls(self) -> None:
        currentHandles = self.__driver.window_handles.copy()
        if set(currentHandles) == set(self.__handleUrlPairs):
            # Tarayıcı ve Selenium'daki sekme sayıları aynıysa aktif sekmeye geçiş yap. Çünkü kullanıcı sekmeler arası geziniyor olabilir.
            activeUserHandle = self.__jsHandler.getActiveTab()
            activeDriverHandle = self.__driver.current_window_handle
            if activeDriverHandle != activeUserHandle:
                self.__driver.switch_to.window(activeUserHandle)
                print(f'Kullanıcı {activeDriverHandle} sekmesinden {activeUserHandle} sekmesine geçiş yaptı!')
                return

            activeDriverHandle = self.__driver.current_window_handle
            activeURL = self.__driver.current_url
            self.__handleUrlPairs[activeDriverHandle] = activeURL

        elif len(currentHandles) < len(self.__handleUrlPairs):
            handlesToBeRemoved = set(self.__handleUrlPairs) - set(currentHandles)
            for handle in handlesToBeRemoved:
                del self.__handleUrlPairs[handle]

        else:  # currentHandles > self.__handleUrlPairs. Yani yeni sekmeler açılmış demektir.
            handlesToBeAdded = set(currentHandles) - set(self.__handleUrlPairs)
            for handle in handlesToBeAdded:
                self.__driver.switch_to.window(handle)
                url = self.__driver.current_url
                # Firefox'da yeni sekme olan 'about:newtab' sayfasında JavaScript çalıştırılamıyor. Bu nedenle Google'a yönlendiriyoruz.
                if url == 'about:newtab':
                    self.__driver.get('https://www.google.com.tr')
                    url = self.__driver.current_url
                self.__handleUrlPairs[handle] = url
                self.__jsHandler.initialEmbeddings()

    def __trackHtmlContentsOfUrls(self):
        self.__contentFetcher.fetchAndPrintHtmlContents(self.__handleUrlPairs)
