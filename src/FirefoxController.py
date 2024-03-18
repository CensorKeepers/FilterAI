from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import threading
from time import sleep
import pathlib
import json

from Logger import Logger
from URLTracker import URLTracker


class FirefoxController():

    def __init__(self) -> 'FirefoxController':
        self.__thread = threading.Thread(target=self.__process, args=())
        self.__tabThread = threading.Thread(target=self.__handleNewTabs, args=())
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
                Logger.warn('[FIREFOX]: Connected to Mozilla Firefox!')
                return True

            except:
                Logger.warn(f'[FIREFOX]: Could not connect to Mozilla Firefox, retrying...')
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
        self.__tabThread.join()

        self.__driver.quit()

    def __handleNewTabs(self) -> None:
        tracker = URLTracker(self.__driver)
        while not self.__shouldTerminate:
            tracker.trackUrls()
            sleep(0.1)

    def start(self) -> None:
        Logger.warn('[FIREFOX]: Firefox controller has been started.')
        self.__thread.start()

    def join(self) -> None:
        self.__thread.join()

    def shouldTerminate(self) -> None:
        self.__shouldTerminate = True