import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from Logger import Logger


class ChromeController():

    def __init__(self) -> 'ChromeController':
        super().__init__()
        self.__driver: webdriver.Chrome = None
        self.__thread = threading.Thread(target=self.__process, args=())

    def __connect(self) -> None:
        chromeOptions = Options()
        chromeOptions.add_experimental_option(
            'debuggerAddress', '127.0.0.1:9921')
        while True:
            try:
                self.__driver = webdriver.Chrome(options=chromeOptions)
                Logger.warn('Connected to Google Chrome!')
                return
            except:
                Logger.warn(
                    f'Could not connect to Google Chrome, retrying...')
                continue

    def __process(self) -> None:
        self.__connect()
        Logger.warn('Closing the Chrome.')
        self.__driver.quit()

    def start(self) -> None:
        self.__thread.start()

    def join(self) -> None:
        self.__thread.join()
