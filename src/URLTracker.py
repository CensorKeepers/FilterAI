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
'''
url değişikliğini bulmak
tab acilip kapandiysa bunu fark edip onlari listeye eklemek cikarmak
html contentleri alirken refresh kontrol et
html'leri al
'''

class URLTracker:
    def __init__(self, driver):
        self.__driver = driver
        self.__handles: List[str] = driver.window_handles.copy()
        self._handleCount = len(self.__handles)
        self.__updateHandlesAndUrls()
        self.__contentFetcher = ContentFetcher(self.__driver)
        self.__contentFetcher.reset()
        self.__lastActiveHandle = ""
        #self._thread = threading.Thread(target=self._process, args=())
        #self._refreshThread = threading.Thread(target=self._handleRefreshs, args=())

        

    def trackUrls(self):
        try:
            currentHandles = self.__driver.window_handles
            original_handle = self.__driver.current_window_handle
            #print(original_handle)
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
            self.__updateHandlesAndUrls()
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
        if self.__driver.current_window_handle in currentHandles:
            self.__driver.switch_to.window(self.__driver.current_window_handle)

        self._handleCount = len(self.__handles)

        
    def __trackHtmlContentsOfUrls(self):
        handles_dict = dict(self.__handles)
        self.__contentFetcher.fetchAndPrintHtmlContents(handles_dict)
        
    #def __getCurrentUrls(self):
    #    return list(self.__handles.values())
    #
    #def __printCurrentTabsAndUrls(self):
    #    print("Aktif Sekmeler ve URL'leri:")
    #    for handle, url in self.__handles.items():
    #        print(f"Sekme: {handle}, URL: {url}")

    #def __process(self) -> None:
    #    self.__refreshThread.start()
    #    self.__refreshThread.join()

    #def start(self) -> None:
    #    self.__thread.start()

    #def join(self) -> None:
    #    self.__thread.join()
    #
    #def __handleRefreshs(self) -> None:
    #    while self.__handleCount != 0:
    #        sleep(0.1)
    
    '''
        def __injectEventListeners(self):
        # Sadece click ve submit olaylarını yakalayacak ve localStorage'a kaydedecek JavaScript kodunu enjekte eder
        js_code = """
        document.body.addEventListener('click', function() {
            localStorage.setItem('lastInteraction', new Date().getTime().toString());
        }, true);
        document.body.addEventListener('submit', function() {
            localStorage.setItem('lastInteraction', new Date().getTime().toString());
        }, true);
        document.body.addEventListener('click', function() {
        var now = new Date();
        var day = now.getDate();
        var month = now.getMonth() + 1; // JavaScript months are 0-based.
        var year = now.getFullYear();
        var hours = now.getHours();
        var minutes = now.getMinutes();
        var seconds = now.getSeconds();
        
        // Format the date and time components to ensure they are in two digits, except the year.
        var formattedDate = day.toString().padStart(2, '0') + '-' + 
                            month.toString().padStart(2, '0') + '-' + 
                            year.toString();
        var formattedTime = hours.toString().padStart(2, '0') + ':' + 
                            minutes.toString().padStart(2, '0') + ':' + 
                            seconds.toString().padStart(2, '0');
        
        // Combine the date and time in your preferred format.
        var dateTimeString = formattedDate + ' ' + formattedTime;
        
        localStorage.setItem('lastInteraction', dateTimeString);
        }, true);
        """
        self.__driver.execute_script(js_code)
                        

                        
                                       try:
                    last_interaction = self.__driver.execute_script("""
        document.body.addEventListener('submit', function() {
            localStorage.setItem('lastInteraction', new Date().getTime().toString());
        }, true);
        document.body.addEventListener('click', function() {
            var now = new Date();
            var day = now.getDate();
            var month = now.getMonth() + 1; // JavaScript months are 0-based.
            var year = now.getFullYear();
            var hours = now.getHours();
            var minutes = now.getMinutes();
            var seconds = now.getSeconds();
            
            // Format the date and time components to ensure they are in two digits, except the year.
            var formattedDate = day.toString().padStart(2, '0') + '-' + 
                                month.toString().padStart(2, '0') + '-' + 
                                year.toString();
            var formattedTime = hours.toString().padStart(2, '0') + ':' + 
                                minutes.toString().padStart(2, '0') + ':' + 
                                seconds.toString().padStart(2, '0');
            
            // Combine the date and time in your preferred format.
            var dateTimeString = formattedDate + ' ' + formattedTime;
            
            localStorage.setItem('lastInteraction', dateTimeString);
        }, true);
        return localStorage.getItem('lastInteraction');""")
                    # Process last_interaction as needed
                    #if last_interaction:
                    #    print(last_interaction)
                    #print(f"last_interaction: {last_interaction}\n")
                except selenium.common.exceptions.JavascriptException as e:
                    pass
                    #Logger.error(f"JavaScript execution failed: {e}")
                    # Handle the exception, e.g., by logging or taking alternative actions
        '''