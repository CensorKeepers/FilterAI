'''
    def __init__(self, driver: Union[webdriver.Edge, webdriver.Chrome, webdriver.Firefox]):
        self.__driver = driver
        self.__handles: List[str] = driver.window_handles.copy()
        self.__handleCount = len(self.__handles)
        self.__urls = {}

        # Başlangıçta açık olan tüm sekmelerin URL'lerini al
        for handle in self.__handles:
            try:
                self.__driver.switch_to.window(handle)
                current_url = self.__driver.current_url
                self.__urls[handle] = current_url
            except Exception as e:
                Logger.error(f"Error switching to window {handle}: {e}")

    def trackUrls(self):
        # Yeni açılan veya kapanan sekmeleri ve URL değişikliklerini izle
        try:
            currentHandles = set(self.__driver.window_handles)
            currentHandleCount = len(currentHandles)

            if self.__handleCount != currentHandleCount:
                newHandles = currentHandles - set(self.__handles)
                closedHandles = set(self.__handles) - currentHandles

                for handle in newHandles:
                    self.__driver.switch_to.window(handle)
                    Logger.warn(f"New tab URL: {self.__driver.current_url}")
                    self.__handles.append(handle)
                    self.__urls[handle] = self.__driver.current_url

                for handle in closedHandles:
                    self.__handles.remove(handle)
                    del self.__urls[handle]

                self.__handleCount = currentHandleCount
            else:
                for handle in self.__handles:
                    self.__driver.switch_to.window(handle)
                    currentUrl = self.__driver.current_url
                    if self.__urls.get(handle, '') != currentUrl:
                        Logger.warn(f"URL changed in tab: {currentUrl}")
                        self.__urls[handle] = currentUrl
        except Exception as e:
            Logger.error(f"An error occurred while tracking URLs: {e}")
        self.printAllOpenUrls()

    def printAllOpenUrls(self):
        # Açık olan tüm URL'leri yazdır
        try:
            for handle in self.__handles:
                self.__driver.switch_to.window(handle)
                Logger.info(f"Open tab URL: {self.__driver.current_url}")
        except Exception as e:
            Logger.error(f"An error occurred while printing all open URLs: {e}")
'''


'''
class URLTracker:
    def __init__(self, driver):
        self.driver = driver
        self.current_urls = {}
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            self.current_urls[handle] = driver.current_url
        self.page_load_times = {handle: self.get_page_load_time() for handle in driver.window_handles}
        self.output_dir = "page_contents"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def get_page_load_time(self):
        return self.driver.execute_script("return window.performance.timing.navigationStart;")

    def trackUrls(self):
        current_handles = set(self.driver.window_handles)
        old_handles = set(self.current_urls.keys())

        # Yeni açılan sekmeler
        new_handles = current_handles - old_handles
        for handle in new_handles:
            self.driver.switch_to.window(handle)
            self.current_urls[handle] = self.driver.current_url
            self.page_load_times[handle] = self.get_page_load_time()
            Logger.warn(f"New tab detected with URL: {self.driver.current_url}")

        # Kapatılan sekmeleri
        closed_handles = old_handles - current_handles
        for handle in closed_handles:
            Logger.warn(f"Tab closed with URL: {self.current_urls[handle]}")
            del self.current_urls[handle]
            del self.page_load_times[handle]

        # Mevcut sekmelerdeki URL değişiklikleri
        for handle in (current_handles & old_handles):
            self.driver.switch_to.window(handle)
            current_url = self.driver.current_url
            page_load_time = self.get_page_load_time()

            if self.current_urls[handle] != current_url:
                Logger.warn(f"URL changed to: {current_url}")
                self.current_urls[handle] = current_url
                self.page_load_times[handle] = page_load_time
            elif self.page_load_times[handle] != page_load_time:
                Logger.warn(f"Page refreshed at: {handle} {self.current_urls[handle]}")
                self.page_load_times[handle] = page_load_time

        self.print_current_urls()
        #self.save_html_content_of_current_page()
'''


'''
YİĞİTHAN

class URLTracker:
    def __init__(self, driver: Union[webdriver.Edge, webdriver.Chrome, webdriver.Firefox]):
        self.__driver = driver
        self.__handles: List[str] = driver.window_handles.copy()
        self.__handleCount = len(self.__handles)

    def trackUrls(self):
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
'''




'''
    def __init__(self, driver):
        self.driver = driver
        self.current_urls = {driver.current_window_handle: driver.current_url}
        self.page_load_times = {driver.current_window_handle: self.get_page_load_time()}
        self.output_dir = "page_contents"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def get_page_load_time(self):
        # Sayfanın navigationStart zamanını döndür
        return self.driver.execute_script("return window.performance.timing.navigationStart;")
    
    def trackUrls(self, duration=120, check_interval=10):
        start_time = time.time()
        while time.time() - start_time < duration:
            current_handles = set(self.driver.window_handles)
            old_handles = set(self.current_urls.keys())

            # Yeni açılan ve kapatılan sekmeleri tespit et
            new_handles = current_handles - old_handles
            closed_handles = old_handles - current_handles

            for handle in new_handles:
                self.driver.switch_to.window(handle)
                self.current_urls[handle] = self.driver.current_url
                self.page_load_times[handle] = self.get_page_load_time()
                Logger.warn(f"New tab detected with URL: {self.driver.current_url}")

            for handle in closed_handles:
                Logger.warn(f"Tab closed with URL: {self.current_urls[handle]}")
                del self.current_urls[handle]
                del self.page_load_times[handle]

            # Mevcut sekmelerdeki URL değişikliklerini ve yenilenmelerini kontrol et
            for handle in (current_handles & old_handles):
                self.driver.switch_to.window(handle)
                current_url = self.driver.current_url
                page_load_time = self.get_page_load_time()

                if self.current_urls[handle] != current_url:
                    Logger.warn(f"URL changed to: {current_url}")
                    self.current_urls[handle] = current_url
                    self.page_load_times[handle] = page_load_time
                elif self.page_load_times[handle] != page_load_time:
                    Logger.warn(f"Page refreshed at: {handle} {self.current_urls[handle]}")
                    self.page_load_times[handle] = page_load_time

            self.print_current_urls()
            #self.save_html_content_of_current_page()
            sleep(check_interval)

    def print_current_urls(self):
        print("-----------------------------------------------------------------")
        print("Currently tracked URLs:")
        for handle, url in self.current_urls.items():
            print(f"Window Handle: {handle}, URL: {url}")            
            
    def save_html_content_of_current_page(self):
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        html_content = self.driver.page_source
        print(html_content)
        print("-----------------------------------------------------------------")
        
        '''