from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import threading
from time import sleep
import pathlib
import json
import socket

from Logger import Logger
from URLTracker import URLTracker


class FirefoxController():

    def __init__(self) -> 'FirefoxController':
        self.__thread = threading.Thread(target=self.__process, args=())
        self.__tabThread = threading.Thread(target=self.__handleNewTabs, args=())
        self.__driver: webdriver.Firefox = None
        self.__webdriverPath: str = ''
        self.__webdriverIp: str = ''
        self.__webdriverPort: int = 0
        self.__remoteIp: str = None
        self.__remotePort: int = 0
        self.__socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__configPath: pathlib.Path = pathlib.Path(str(pathlib.Path(__file__).parent.parent) + '/config/FirefoxController.json')
        self.__config: dict = None
        self.__shouldTerminate: bool = False
        self.__readAndApplyConfigFile()
        self.__configureController()

    def __connectToBrowser(self) -> bool:
        serviceArgs = ['--marionette-port', str(self.__webdriverPort), '--connect-existing']
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
        self.__webdriverIp = self.__config['webdriverIp']
        self.__webdriverPort = self.__config['webdriverPort']
        self.__webdriverPath = self.__config['webdriverPath']
        self.__remoteIp = self.__config['remoteIp']
        self.__remotePort = self.__config['remotePort']

    def __process(self) -> None:
        if not self.__connectToBrowser():
            return

        while True:
            try:
                self.__socket.connect((self.__remoteIp, self.__remotePort))
                Logger.warn(f'[FIREFOX]: Connected to remote server {self.__remoteIp}:{self.__remotePort}.')
                break
            except:
                Logger.warn(f'[FIREFOX]: Could not connect to the remote server. Retrying...')
                continue

        self.__driver.get('https://www.google.com.tr')
        self.__tabThread.start()
        self.__tabThread.join()

        self.__driver.quit()

    def __handleNewTabs(self) -> None:
        tracker = URLTracker(self.__driver)
        while not self.__shouldTerminate:
            tracker.trackUrls(self.__socket)
            sleep(0)

    def start(self) -> None:
        self.__thread.start()
        Logger.warn('[FIREFOX]: Firefox controller has been started.')

    def join(self) -> None:
        self.__thread.join()

    def shouldTerminate(self) -> None:
        self.__shouldTerminate = True
