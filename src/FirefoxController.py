import threading
import pathlib
import json
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

from Logger import Logger

from time import sleep

from URLTracker import URLTracker

class FirefoxController():

    def __init__(self) -> 'FirefoxController':
        self.__thread = threading.Thread(target=self.__process, args=())
        self.__tabThread = threading.Thread(target=self.__handleNewTabs, args=())
        self.__refreshThread = threading.Thread(target=self.__handleRefreshs, args=())
        self.__sensorThread = threading.Thread(target=self.__handleHTMLchanges, args=())
        self.__driver: webdriver.Firefox = None
        self.__webdriverPath: str = ''
        self.__ip: str = ''
        self.__port: int = 0
        self.__configPath: pathlib.Path = pathlib.Path(str(pathlib.Path(__file__).parent.parent) + '/config/FirefoxController.json')
        self.__config: dict = None
        self.__shouldTerminate: bool = False
        self.__readAndApplyConfigFile()
        self.__configureController()

    def __connectToBrowser(self) -> bool:
        serviceArgs = ['--marionette-port', str(self.__port), '--connect-existing']
        firefoxService = Service(executable_path=self.__webdriverPath, port=3000, service_args=serviceArgs)

        while not self.__shouldTerminate:
            try:
                self.__driver = webdriver.Firefox(service=firefoxService)
                Logger.warn('Connected to Mozilla Firefox!')
                return True

            except:
                Logger.warn(f'Could not connect to Mozilla Firefox, retrying...')
                continue

        return False

    def __readAndApplyConfigFile(self) -> None:
        file = open(self.__configPath, mode='r', encoding='utf-8')
        self.__config = json.load(file)
        file.close()

    def __configureController(self) -> None:
        self.__ip = self.__config['ip']
        self.__port = self.__config['port']
        self.__webdriverPath = self.__config['webdriverPath']

    def __process(self) -> None:
        if not self.__connectToBrowser():
            return

        self.__driver.get('https://www.google.com.tr')
        self.__tabThread.start()
        self.__refreshThread.start()
        self.__sensorThread.start()

        self.__tabThread.join()
        self.__refreshThread.join()
        self.__sensorThread.join()

    def __handleNewTabs(self) -> None:
        while not self.__shouldTerminate:
            tracker = URLTracker(self.__driver)
            tracker.track_new_tabs()
            sleep(0.1)

    def __handleRefreshs(self) -> None:
        while not self.__shouldTerminate:
            sleep(0.1)

    def __handleHTMLchanges(self) -> None:
        while not self.__shouldTerminate:
            sleep(0.1)


    def start(self) -> None:
        self.__thread.start()

    def join(self) -> None:
        self.__thread.join()

    def shouldTerminate(self) -> None:
        self.__shouldTerminate = True

