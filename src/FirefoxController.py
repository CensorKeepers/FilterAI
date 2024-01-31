import threading
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

from Logger import Logger


class FirefoxController():

    def __init__(self) -> 'FirefoxController':
        super().__init__()
        self.__driver: webdriver.Firefox = None
        self.__thread = threading.Thread(target=self.__process, args=())

    def __connect(self) -> None:
        firefoxService = Service(executable_path='/home/ubuntu/webdrivers/geckodriver', port=3000, service_args=[
                                 '--marionette-port', '2828', '--connect-existing'])
        while True:
            try:
                self.__driver = webdriver.Firefox(service=firefoxService)
                Logger.warn('Connected to Mozilla Firefox!')
                return
            except:
                Logger.warn(
                    f'Could not connect to Mozilla Firefox, retrying...')
                continue

    def __process(self) -> None:
        self.__connect()
        Logger.warn('Closing the Firefox.')
        self.__driver.quit()

    def start(self) -> None:
        self.__thread.start()

    def join(self) -> None:
        self.__thread.join()
